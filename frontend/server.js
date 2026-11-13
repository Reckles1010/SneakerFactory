/* MERCURY - SERVIDOR (Node + Express + PostgreSQL + Odoo) */

const express = require("express");
const { Pool } = require("pg");
const bcrypt = require("bcrypt");
const dotenv = require("dotenv");
const path = require("path");
const crypto = require("crypto");


/* CONFIGURACIÓN */

dotenv.config({ path: path.join(__dirname, ".env") });

const PORT = Number(process.env.PORT || 3001);
const SALT_ROUNDS = 10;
const MIN_PASSWORD_LENGTH = 8;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/* Genera ids de texto para Clientes, Pedido y Linea de pedido (ej: CLI-3f9a1b2c) */
const nuevoId = (prefijo) => `${prefijo}-${crypto.randomUUID().slice(0, 8)}`;

const app = express();

app.use(express.json());


/* POSTGRESQL */

const db = new Pool({
    host: process.env.DB_HOST || "localhost",
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_NAME || "Mercury",
    user: process.env.DB_USER || "postgres",
    password: process.env.DB_PASSWORD
});

/* Comprueba la conexión y adapta las tablas existentes a la web */
async function inicializarBaseDeDatos() {

    await db.query("SELECT 1");

    /* El registro web no pide dirección */
    await db.query(`ALTER TABLE "Clientes" ALTER COLUMN direccion DROP NOT NULL`);

    /* Datos de envío del pedido web (opcionales) */
    await db.query(`ALTER TABLE "Pedido" ADD COLUMN IF NOT EXISTS direccion_envio TEXT`);
    await db.query(`ALTER TABLE "Pedido" ADD COLUMN IF NOT EXISTS notas TEXT`);

    /* Correo único para detectar duplicados */
    try {
        await db.query(
            `CREATE UNIQUE INDEX IF NOT EXISTS clientes_correo_uq ON "Clientes" (correo)`
        );
    } catch (error) {
        console.warn("No se pudo crear el índice único de correo:", error.message);
    }
}


/* ODOO 19 - API JSON-2 */

const ODOO_URL = process.env.ODOO_URL;
const ODOO_DB = process.env.ODOO_DB;
const ODOO_API_KEY = process.env.ODOO_API_KEY;

async function consultarOdoo(modelo, metodo, datos = {}) {

    if (!ODOO_URL || !ODOO_API_KEY) {
        throw new Error("Falta configurar ODOO_URL u ODOO_API_KEY");
    }

    const respuesta = await fetch(
        `${ODOO_URL.replace(/\/$/, "")}/json/2/${modelo}/${metodo}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `bearer ${ODOO_API_KEY}`,
                ...(ODOO_DB ? { "X-Odoo-Database": ODOO_DB } : {})
            },
            body: JSON.stringify(datos)
        }
    );

    if (!respuesta.ok) {
        const error = await respuesta.text();
        throw new Error(`Error API Odoo (${respuesta.status}): ${error}`);
    }

    return await respuesta.json();
}


/* ARCHIVOS ESTÁTICOS */

app.use("/css", express.static(path.join(__dirname, "css")));
app.use("/js", express.static(path.join(__dirname, "js")));
app.use("/assets", express.static(path.join(__dirname, "assets")));
app.use(express.static(path.join(__dirname, "views")));

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "inicio.html"));
});


/* API - AUTENTICACIÓN (tabla Clientes) */

    /* Registro de usuarios */
app.post("/api/auth/register", async (req, res) => {

    try {
        const { nombre, apellidos, email, password } = req.body;

        const nombreLimpio = String(nombre || "").trim();
        const apellidosLimpios = String(apellidos || "").trim();
        const emailLimpio = String(email || "").trim().toLowerCase();
        const passwordRecibida = String(password || "");

        if (!nombreLimpio || !apellidosLimpios) {
            return res.status(400).json({
                message: "El nombre y los apellidos son obligatorios."
            });
        }

        if (!EMAIL_REGEX.test(emailLimpio)) {
            return res.status(400).json({
                message: "Introduce un correo electrónico válido."
            });
        }

        if (passwordRecibida.length < MIN_PASSWORD_LENGTH) {
            return res.status(400).json({
                message: `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres.`
            });
        }

        /* Correo duplicado */
        const existente = await db.query(
            `SELECT 1 FROM "Clientes" WHERE correo = $1`,
            [emailLimpio]
        );

        if (existente.rowCount > 0) {
            return res.status(409).json({
                message: "Ese correo ya está registrado."
            });
        }

        const hash = await bcrypt.hash(passwordRecibida, SALT_ROUNDS);

        await db.query(
            `INSERT INTO "Clientes" (id_cliente, nombre, correo, password_hash)
            VALUES ($1, $2, $3, $4)`,
            [nuevoId("CLI"), `${nombreLimpio} ${apellidosLimpios}`, emailLimpio, hash]
        );

        res.status(201).json({ ok: true });

    } catch (error) {

        console.error("Error registro:", error.message);

        /* 23505 = correo duplicado (UNIQUE) */
        if (error.code === "23505") {
            return res.status(409).json({
                message: "Ese correo ya está registrado."
            });
        }

        res.status(500).json({ message: "Error del servidor." });
    }
});

    /* Inicio de sesión */
app.post("/api/auth/login", async (req, res) => {

    try {
        const emailLimpio = String(req.body.email || "").trim().toLowerCase();
        const passwordRecibida = String(req.body.password || "");

        const resultado = await db.query(
            `SELECT id_cliente AS id, nombre, correo AS email, password_hash
            FROM "Clientes"
            WHERE correo = $1`,
            [emailLimpio]
        );

        const usuario = resultado.rows[0];

        const credencialesValidas =
            usuario &&
            usuario.password_hash &&
            await bcrypt.compare(passwordRecibida, usuario.password_hash);

        if (!credencialesValidas) {
            return res.status(401).json({
                message: "Correo o contraseña incorrectos."
            });
        }

        delete usuario.password_hash;

        /* El nombre completo va en "nombre" */
        usuario.apellidos = "";
        usuario.rol = "cliente";

        res.json({ user: usuario });

    } catch (error) {

        console.error("Error login:", error.message);

        res.status(500).json({ message: "Error del servidor." });
    }
});


/* API - PEDIDOS (tablas Pedido y Linea de pedido) */

/* Limpia el DNI/NIE: mayúsculas y sin espacios ni guiones */
function normalizarDni(dni) {
    return String(dni || "").toUpperCase().replace(/[\s-]/g, "");
}

/* Valida DNI (8 números + letra) o NIE (X/Y/Z + 7 números + letra) */
function dniValido(dni) {
    if (!/^([0-9]{8}|[XYZ][0-9]{7})[A-Z]$/.test(dni)) return false;

    const numero = dni
        .slice(0, -1)
        .replace("X", "0")
        .replace("Y", "1")
        .replace("Z", "2");

    return "TRWAGMYFPDXBNJZSQVHLCKE"[Number(numero) % 23] === dni.slice(-1);
}

/* Extrae el número de una talla ("42", "35-38", "Zapatillas 42 · ...") */
function tallaNumerica(talla) {
    const coincidencia = String(talla || "").match(/\d+/);
    return coincidencia ? Number(coincidencia[0]) : 0;
}

/* Color de una zona según la personalización del Custom Lab */
function colorDe(personalizacion, zona) {
    const colores = personalizacion.product === "sock"
        ? (personalizacion.sockColors || {})
        : (personalizacion.colors || {});

    return colores[zona] ? String(colores[zona]) : "Estándar";
}

app.post("/api/pedidos", async (req, res) => {

    const client = await db.connect();

    try {
        const { usuarioId, destinatario, productos } = req.body;

        if (!usuarioId || !destinatario || !Array.isArray(productos) || productos.length === 0) {
            return res.status(400).json({ message: "Pedido no válido." });
        }

        const dni = normalizarDni(destinatario.dni);

        if (!dniValido(dni)) {
            return res.status(400).json({ message: "Introduce un DNI o NIE válido." });
        }

        const cliente = await client.query(
            `SELECT id_cliente FROM "Clientes" WHERE id_cliente = $1`,
            [String(usuarioId)]
        );

        if (cliente.rowCount === 0) {
            return res.status(401).json({ message: "Debes iniciar sesión para comprar." });
        }

        const direccionEnvio = [
            destinatario.address,
            destinatario.number,
            destinatario.postalCode,
            destinatario.city,
            destinatario.province
        ].filter(Boolean).join(", ");

        await client.query("BEGIN");

        /* El DNI se guarda en la ficha del cliente */
        await client.query(
            `UPDATE "Clientes" SET dni = $1 WHERE id_cliente = $2`,
            [dni, String(usuarioId)]
        );

        const pedidosIds = [];
        let total = 0;

        /* Cada producto del carrito genera una línea y un pedido */
        for (const p of productos) {

            const cantidad = Math.max(1, Number(p.quantity) || 1);
            const precioLinea = (Number(p.price) || 0) * cantidad;
            const c = p.customization || {};

            const idLinea = nuevoId("LIN");
            const idPedido = nuevoId("PED");

            await client.query(
                `INSERT INTO "Linea de pedido"
                    (id_linea, talla, cantidad, "colorBase", "colorPanel",
                    "colorSuela", "colorCordones", "PrecioTotal")
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
                [
                    idLinea,
                    tallaNumerica(p.size),
                    cantidad,
                    colorDe(c, "main"),
                    colorDe(c, "panel"),
                    colorDe(c, "sole"),
                    colorDe(c, "laces"),
                    precioLinea.toFixed(2)
                ]
            );

            await client.query(
                `INSERT INTO "Pedido"
                    (id_pedido, tipo, estado, descuento, fecha,
                    "id_linea_Linea de pedido", "id_modelo_Modelo", "id_cliente_Clientes",
                    direccion_envio, notas)
                VALUES ($1, $2, $3, $4, CURRENT_DATE, $5, $6, $7, $8, $9)`,
                [
                    idPedido,
                    p.customization ? "Personalizado" : "Estándar",
                    "Pendiente",
                    false,
                    idLinea,
                    String(p.id || ""),
                    String(usuarioId),
                    direccionEnvio,
                    destinatario.notes || null
                ]
            );

            pedidosIds.push(idPedido);
            total += precioLinea;
        }

        await client.query("COMMIT");

        res.status(201).json({
            ok: true,
            pedidoId: pedidosIds[0],
            pedidos: pedidosIds,
            total
        });

    } catch (error) {

        await client.query("ROLLBACK").catch(() => {});

        console.error("Error pedido:", error.message);

        res.status(500).json({ message: "No se pudo registrar el pedido." });

    } finally {
        client.release();
    }
});


/* API - MERCURY (POSTGRESQL) */

app.get("/api/productos", async (req, res) => {

    try {
        const resultado = await db.query(`
            SELECT id_modelo AS id, nombre, precio, stock
            FROM "Modelo"
            ORDER BY id_modelo
        `);

        res.json(resultado.rows);

    } catch (error) {

        console.error("Error productos:", error.message);

        res.status(500).json({
            error: "No se pudieron obtener los productos"
        });
    }
});

app.get("/api/estado-db", async (req, res) => {

    try {
        const resultado = await db.query("SELECT NOW() AS fecha");

        res.json({
            conectado: true,
            fecha: resultado.rows[0].fecha
        });

    } catch (error) {

        console.error("Error PostgreSQL:", error.message);

        res.status(500).json({
            conectado: false,
            error: error.message
        });
    }
});


/* API - ODOO */

app.get("/api/odoo/estado", async (req, res) => {

    try {
        const resultado = await consultarOdoo("res.users", "context_get");

        res.json({
            conectado: true,
            mensaje: "Conexión con Odoo 19 correcta",
            datos: resultado
        });

    } catch (error) {

        console.error("Error Odoo:", error.message);

        res.status(500).json({
            conectado: false,
            error: error.message
        });
    }
});

app.get("/api/odoo/clientes", async (req, res) => {

    try {
        const clientes = await consultarOdoo("res.partner", "search_read", {
            domain: [["customer_rank", ">", 0]],
            fields: ["id", "name", "email", "phone"],
            limit: 50
        });

        res.json(clientes);

    } catch (error) {

        console.error("Error clientes Odoo:", error.message);

        res.status(500).json({
            error: "No se pudieron obtener los clientes de Odoo"
        });
    }
});


/* INICIAR SERVIDOR */

async function iniciarServidor() {

    let postgresOk = false;

    try {
        await inicializarBaseDeDatos();
        postgresOk = true;
    } catch (error) {
        console.error("No se pudo preparar PostgreSQL:", error.message);
    }

    app.listen(PORT, () => {
        console.log("MERCURY - SERVIDOR INICIADO");
        console.log(`Servidor: http://localhost:${PORT}`);
        console.log(`PostgreSQL: ${postgresOk ? "conectado" : "NO disponible"}`);
        console.log(
            ODOO_URL && ODOO_API_KEY
                ? "Odoo 19: API JSON-2 configurada"
                : "Odoo 19: sin configurar (faltan variables en .env)"
        );
    });
}

iniciarServidor();