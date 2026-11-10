/* MERCURY - SERVIDOR (Node + Express + PostgreSQL + Odoo) */

const express = require("express");
const { Pool } = require("pg");
const bcrypt = require("bcrypt");
const dotenv = require("dotenv");
const path = require("path");


/* CONFIGURACIÓN */

dotenv.config({ path: path.join(__dirname, ".env") });

const PORT = Number(process.env.PORT || 3001);
const SALT_ROUNDS = 10;
const MIN_PASSWORD_LENGTH = 8;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const app = express();

app.use(express.json());


/* POSTGRESQL */

const db = new Pool({
    host: process.env.DB_HOST || "localhost",
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_NAME || "Mercury",
    user: process.env.DB_USER || "D@m1234",
    password: process.env.DB_PASSWORD
});


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


/* API - AUTENTICACIÓN */

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

        const hash = await bcrypt.hash(passwordRecibida, SALT_ROUNDS);

        await db.query(
            `INSERT INTO usuarios (nombre, apellidos, email, password_hash)
            VALUES ($1, $2, $3, $4)`,
            [nombreLimpio, apellidosLimpios, emailLimpio, hash]
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
            `SELECT id, nombre, apellidos, email, rol, password_hash
             FROM usuarios
             WHERE email = $1`,
            [emailLimpio]
        );

        const usuario = resultado.rows[0];

        const credencialesValidas =
            usuario &&
            await bcrypt.compare(passwordRecibida, usuario.password_hash);

        if (!credencialesValidas) {
            return res.status(401).json({
                message: "Correo o contraseña incorrectos."
            });
        }

        delete usuario.password_hash;

        res.json({ user: usuario });

    } catch (error) {

        console.error("Error login:", error.message);

        res.status(500).json({ message: "Error del servidor." });
    }
});


/* API - PEDIDOS*/

app.post("/api/pedidos", async (req, res) => {

    const client = await db.connect();

    try {
        const { usuarioId, destinatario, productos } = req.body;

        if (!usuarioId || !destinatario || !Array.isArray(productos) || productos.length === 0) {
            return res.status(400).json({ message: "Pedido no válido." });
        }

        const usuario = await client.query(
            "SELECT id FROM usuarios WHERE id = $1",
            [usuarioId]
        );

        if (usuario.rowCount === 0) {
            return res.status(401).json({ message: "Debes iniciar sesión para comprar." });
        }

        const total = productos.reduce((suma, p) => {
            return suma + (Number(p.price) || 0) * Math.max(1, Number(p.quantity) || 1);
        }, 0);

        await client.query("BEGIN");

        const pedido = await client.query(
            `INSERT INTO pedidos
                (usuario_id, nombre, email, telefono, direccion, numero,
                codigo_postal, ciudad, provincia, notas, total)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id`,
            [
                usuarioId,
                destinatario.name,
                destinatario.email,
                destinatario.phone || null,
                destinatario.address,
                destinatario.number || null,
                destinatario.postalCode,
                destinatario.city,
                destinatario.province,
                destinatario.notes || null,
                total.toFixed(2)
            ]
        );

        const pedidoId = pedido.rows[0].id;

        for (const p of productos) {
            await client.query(
                `INSERT INTO pedido_lineas
                    (pedido_id, producto_id, nombre, talla, precio, cantidad, personalizacion)
                VALUES ($1, $2, $3, $4, $5, $6, $7)`,
                [
                    pedidoId,
                    String(p.id || ""),
                    p.name,
                    p.size || null,
                    Number(p.price) || 0,
                    Math.max(1, Number(p.quantity) || 1),
                    p.customization ? JSON.stringify(p.customization) : null
                ]
            );
        }

        await client.query("COMMIT");

        res.status(201).json({ ok: true, pedidoId, total });

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

    try {
        await inicializarBaseDeDatos();
    } catch (error) {
        console.error("No se pudo preparar PostgreSQL:", error.message);
    }

    app.listen(PORT, () => {
        console.log("MERCURY - SERVIDOR INICIADO");
        console.log(`Servidor: http://localhost:${PORT}`);
        console.log("PostgreSQL: configurado");
        console.log("Odoo 19: API JSON-2 configurada");
    });
}

iniciarServidor();