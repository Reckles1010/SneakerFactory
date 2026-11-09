package psp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class Informe {

    public static void main(String[] args) {

        if (args.length < 1) {
            System.err.println("ERROR: falta la ruta del informe");
            System.exit(2);
        }
        Path rutaInforme = Path.of(args[0]);

        List<String> informe = new ArrayList<>();
        informe.add("INFORME DE PROCESAMIENTO");
        informe.add("Generado: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss")));
        informe.add("");

        try {
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            String linea;
            while ((linea = entrada.readLine()) != null) {
                informe.add(linea);
            }
            Files.write(rutaInforme, informe, StandardCharsets.UTF_8);

        } catch (IOException e) {
            System.err.println("ERROR: no se pudo generar el informe en " + rutaInforme);
            System.exit(2);
        }

        System.out.println("Informe generado en " + rutaInforme);
        System.exit(0);
    }
}