package psp;

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

    private static final int TIMEOUT_SEGUNDOS = 10;

    private static final List<String> log = new ArrayList<>();

    static class Resultado {
        int codigo;
        String salida = "";
        String errores = "";
        boolean timeout = false;
    }

    public static void main(String[] args) {

        if (args.length != 4) {
            System.err.println("Uso: Coordinador <ruta_csv> <total_pares> <talla_min> <talla_max>");
            return;
        }

        String ruta = args[0];
        String total = args[1];
        String tallaMin = args[2];
        String tallaMax = args[3];

        Path rutaPedido = Path.of(ruta);
        String contenidoPedido;
        try {
            contenidoPedido = Files.readString(rutaPedido, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo leer el fichero " + rutaPedido);
            return;
        }

        String idPedido = obtenerIdPedido(contenidoPedido);

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

        Resultado validacion = ejecutarHijo("Validador", contenidoPedido, total, tallaMin, tallaMax);
        if (validacion.codigo != 0) {
            System.out.println("Pedido " + idPedido + " rechazado, no se lanzan más procesos");
            registrar("Procesamiento detenido porque el Validador terminó con código " + validacion.codigo);
            guardarLog(rutaLog);
            return;
        }

        Resultado resumen = ejecutarHijo("ResumenTallas", contenidoPedido);

        Resultado ficha = ejecutarHijo("FichaTaller", contenidoPedido, rutaFicha.toString());

        String datosInforme = "Pedido " + idPedido + " (" + rutaPedido + ")\n\n"
                + bloque("Validador", validacion) + "\n"
                + bloque("ResumenTallas", resumen) + "\n"
                + bloque("FichaTaller", ficha);
        Resultado informe = ejecutarHijo("Informe", datosInforme, rutaInforme.toString());

        boolean todoCorrecto = resumen.codigo == 0 && ficha.codigo == 0 && informe.codigo == 0;
        String mensajeFinal = todoCorrecto ? "completado correctamente" : "completado con incidencias";

        System.out.println("Pedido " + idPedido + " " + mensajeFinal);
        registrar("Fin del procesamiento, " + mensajeFinal);
        guardarLog(rutaLog);
    }

    private static Resultado ejecutarHijo(String clase, String entrada, String... argumentos) {

        Resultado r = new Resultado();
        long inicio = System.currentTimeMillis();

        List<String> comando = new ArrayList<>();
        comando.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
        comando.add("-Dstdout.encoding=UTF-8");
        comando.add("-Dstderr.encoding=UTF-8");
        comando.add("-cp");
        comando.add(System.getProperty("java.class.path"));
        comando.add("psp." + clase);
        comando.addAll(List.of(argumentos));

        File ficheroSalida = null;
        File ficheroErrores = null;

        try {
            ficheroSalida = File.createTempFile("psp_" + clase + "_out", ".txt");
            ficheroErrores = File.createTempFile("psp_" + clase + "_err", ".txt");

            ProcessBuilder pb = new ProcessBuilder(comando);
            pb.redirectOutput(ficheroSalida);
            pb.redirectError(ficheroErrores);

            Process proceso = pb.start();

            try (BufferedWriter alHijo = new BufferedWriter(
                    new OutputStreamWriter(proceso.getOutputStream(), StandardCharsets.UTF_8))) {
                alHijo.write(entrada);
            } catch (IOException e) {
            }

            boolean terminado = proceso.waitFor(TIMEOUT_SEGUNDOS, TimeUnit.SECONDS);
            if (terminado) {
                r.codigo = proceso.exitValue();
            } else {
                proceso.destroyForcibly();
                proceso.waitFor();
                r.timeout = true;
                r.codigo = -1;
            }

            r.salida = new String(Files.readAllBytes(ficheroSalida.toPath()), StandardCharsets.UTF_8);
            r.errores = new String(Files.readAllBytes(ficheroErrores.toPath()), StandardCharsets.UTF_8);

        } catch (IOException e) {
            r.codigo = -2;
            r.errores = "No se pudo lanzar el proceso -> " + e.getMessage();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            r.codigo = -3;
            r.errores = "Se interrumpió la espera del proceso";
        } finally {
            if (ficheroSalida != null) ficheroSalida.delete();
            if (ficheroErrores != null) ficheroErrores.delete();
        }

        long duracion = System.currentTimeMillis() - inicio;

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

    private static String obtenerIdPedido(String contenido) {
        String[] lineas = contenido.split("\\R");
        if (lineas.length > 1) {
            String id = lineas[1].split(";")[0].trim();
            if (!id.isEmpty()) {
                return id.replaceAll("[^A-Za-z0-9_-]", "_");
            }
        }
        return "SIN_ID";
    }

    private static String bloque(String clase, Resultado r) {
        return "## " + clase + " (código " + r.codigo + ")\n" + r.salida.trim() + "\n";
    }

    private static void registrar(String mensaje) {
        String hora = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        log.add("[" + hora + "] " + mensaje);
    }

    private static void guardarLog(Path rutaLog) {
        try {
            Files.write(rutaLog, log, StandardCharsets.UTF_8);
            System.out.println("Log guardado en " + rutaLog);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo guardar el log en " + rutaLog);
        }
    }
}