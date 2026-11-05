package psp; //La clase Coordinador está en el paquete psp.

import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class Coordinador {

    //Tiempo máximo en segundos que se espera a cada proceso hijo antes de pararlo
    private static final int TIMEOUT_SEGUNDOS = 10;

    //Líneas del log que se guardarán en un fichero al terminar
    private static final List<String> log = new ArrayList<>();

    //Guarda lo que devuelve un proceso hijo, su código de salida, su salida estándar y su salida de error
    static class Resultado {
        int codigo;
        String salida = "";
        String errores = "";
        boolean timeout = false;
    }

    public static void main(String[] args) {

        //Datos del pedido que se reciben como argumentos (ruta total tallaMin tallaMax), son obligatorios porque cambian en cada pedido
        if (args.length != 4) {
            System.err.println("Uso: Coordinador <ruta_csv> <total_pares> <talla_min> <talla_max>");
            return;
        }

        String ruta = args[0];
        String total = args[1];
        String tallaMin = args[2];
        String tallaMax = args[3];

        //Lee el pedido entero como texto para enviárselo a los procesos hijos por su entrada estándar
        Path rutaPedido = Path.of(ruta);
        String contenidoPedido;
        try {
            contenidoPedido = Files.readString(rutaPedido, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo leer el fichero " + rutaPedido);
            return;
        }

        //Saca el número de pedido del propio CSV para nombrar los ficheros de salida
        String idPedido = obtenerIdPedido(contenidoPedido);

        //Crea la carpeta de salida si no existe
        Path carpetaSalida = Path.of("salida");
        try {
            Files.createDirectories(carpetaSalida);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo crear la carpeta de salida");
            return;
        }

        Path rutaFicha = carpetaSalida.resolve("ficha_" + idPedido + ".txt");
        Path rutaInforme = carpetaSalida.resolve("informe_" + idPedido + ".txt");
        Path rutaLog = carpetaSalida.resolve("log_" + idPedido + ".txt");

        System.out.println("Procesando pedido " + idPedido + " (" + rutaPedido + ")");
        registrar("Inicio del procesamiento del pedido " + idPedido + " desde " + rutaPedido);

        //1 Validador, si el pedido no es válido no tiene sentido lanzar el resto de procesos
        Resultado validacion = ejecutarHijo("Validador", contenidoPedido, total, tallaMin, tallaMax);
        if (validacion.codigo != 0) {
            System.out.println("Pedido " + idPedido + " rechazado, no se lanzan más procesos");
            registrar("Procesamiento detenido porque el Validador terminó con código " + validacion.codigo);
            guardarLog(rutaLog);
            return;
        }

        //2 Resumen de cantidades por talla
        Resultado resumen = ejecutarHijo("ResumenTallas", contenidoPedido);

        //3 Ficha para el taller, se le pasa la ruta donde debe guardarla
        Resultado ficha = ejecutarHijo("FichaTaller", contenidoPedido, rutaFicha.toString());

        //4 Informe, recibe por su entrada estándar los resultados de los procesos anteriores
        String datosInforme = "Pedido " + idPedido + " (" + rutaPedido + ")\n\n"
                + bloque("Validador", validacion) + "\n"
                + bloque("ResumenTallas", resumen) + "\n"
                + bloque("FichaTaller", ficha);
        Resultado informe = ejecutarHijo("Informe", datosInforme, rutaInforme.toString());

        //El procesamiento es correcto solo si todos los procesos han terminado con código 0
        boolean todoCorrecto = resumen.codigo == 0 && ficha.codigo == 0 && informe.codigo == 0;
        String mensajeFinal = todoCorrecto ? "completado correctamente" : "completado con incidencias";

        System.out.println("Pedido " + idPedido + " " + mensajeFinal);
        registrar("Fin del procesamiento, " + mensajeFinal);
        guardarLog(rutaLog);
    }

    //Lanza una clase del paquete psp como proceso hijo, le envía datos por su entrada estándar y recoge su resultado
    private static Resultado ejecutarHijo(String clase, String entrada, String... argumentos) {

        Resultado r = new Resultado();
        long inicio = System.currentTimeMillis();

        //Comando para lanzar el hijo con el mismo java y classpath que el coordinador, como en una terminal
        List<String> comando = new ArrayList<>();
        comando.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
        comando.add("-Dstdout.encoding=UTF-8"); //El hijo escribe en UTF-8, la misma codificación con la que lee el padre
        comando.add("-Dstderr.encoding=UTF-8");
        comando.add("-cp");
        comando.add(System.getProperty("java.class.path"));
        comando.add("psp." + clase);
        comando.addAll(List.of(argumentos));

        File ficheroSalida = null;
        File ficheroErrores = null;

        try {
            //La salida y los errores del hijo se redirigen a ficheros temporales para que el padre no se bloquee leyendo y pueda aplicar el timeout
            ficheroSalida = File.createTempFile("psp_" + clase + "_out", ".txt");
            ficheroErrores = File.createTempFile("psp_" + clase + "_err", ".txt");

            ProcessBuilder pb = new ProcessBuilder(comando);
            pb.redirectOutput(ficheroSalida);
            pb.redirectError(ficheroErrores);

            Process proceso = pb.start(); //Aquí se crea el proceso hijo

            //Envía los datos por la entrada estándar del hijo y la cierra para que sepa que no hay más
            try (BufferedWriter alHijo = new BufferedWriter(
                    new OutputStreamWriter(proceso.getOutputStream(), StandardCharsets.UTF_8))) {
                alHijo.write(entrada);
            } catch (IOException e) {
                //Si el hijo ya ha terminado no puede recibir datos, su código de salida indicará el motivo
            }

            //Espera al hijo un tiempo máximo, si no termina a tiempo se fuerza su finalización
            boolean terminado = proceso.waitFor(TIMEOUT_SEGUNDOS, TimeUnit.SECONDS);
            if (terminado) {
                r.codigo = proceso.exitValue();
            } else {
                proceso.destroyForcibly();
                proceso.waitFor();
                r.timeout = true;
                r.codigo = -1;
            }

            //Recoge lo que el hijo ha escrito por su salida estándar y por su salida de error
            r.salida = new String(Files.readAllBytes(ficheroSalida.toPath()), StandardCharsets.UTF_8);
            r.errores = new String(Files.readAllBytes(ficheroErrores.toPath()), StandardCharsets.UTF_8);

        } catch (IOException e) { //Fallo al crear el proceso o los ficheros temporales
            r.codigo = -2;
            r.errores = "No se pudo lanzar el proceso -> " + e.getMessage();
        } catch (InterruptedException e) { //Se interrumpió al padre mientras esperaba
            Thread.currentThread().interrupt();
            r.codigo = -3;
            r.errores = "Se interrumpió la espera del proceso";
        } finally {
            //Borra los ficheros temporales pase lo que pase
            if (ficheroSalida != null) ficheroSalida.delete();
            if (ficheroErrores != null) ficheroErrores.delete();
        }

        long duracion = System.currentTimeMillis() - inicio;

        //Muestra por consola lo que ha devuelto el hijo, separando la salida normal de los errores
        for (String linea : r.salida.split("\\R")) {
            if (!linea.isBlank()) System.out.println("[" + clase + "] " + linea);
        }
        for (String linea : r.errores.split("\\R")) {
            if (!linea.isBlank()) System.err.println("[" + clase + " ERROR] " + linea);
        }

        String estado = r.timeout ? "TIMEOUT" : (r.codigo == 0 ? "OK" : "FALLO");
        System.out.println("[" + clase + "] terminó con código " + r.codigo + " (" + estado + ") en " + duracion + " ms");
        registrar(clase + " -> código " + r.codigo + " " + estado + " (" + duracion + " ms)");

        return r;
    }

    //Devuelve el número de pedido de la primera fila de datos, o SIN_ID si no se puede obtener
    private static String obtenerIdPedido(String contenido) {
        String[] lineas = contenido.split("\\R");
        if (lineas.length > 1) {
            String id = lineas[1].split(";")[0].trim();
            if (!id.isEmpty()) {
                return id.replaceAll("[^A-Za-z0-9_-]", "_"); //Quito carácter no válidos en nombres de fichero
            }
        }
        return "SIN_ID";
    }

    //Da formato al resultado de un proceso para incluirlo en el informe
    private static String bloque(String clase, Resultado r) {
        return "## " + clase + " (código " + r.codigo + ")\n" + r.salida.trim() + "\n";
    }

    //Añade una línea al log con la hora actual
    private static void registrar(String mensaje) {
        String hora = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        log.add("[" + hora + "] " + mensaje);
    }

    //Escribe todas las líneas del log en un fichero
    private static void guardarLog(Path rutaLog) {
        try {
            Files.write(rutaLog, log, StandardCharsets.UTF_8);
            System.out.println("Log guardado en " + rutaLog);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo guardar el log en " + rutaLog);
        }
    }
}