package psp; //La clase FichaTaller está en el paquete psp.

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
import java.util.Map;
import java.util.TreeMap;

public class FichaTaller {

    public static void main(String[] args) {

        //La ruta donde se guardará la ficha la envía el coordinador como argumento
        if (args.length < 1) {
            System.err.println("ERROR: falta la ruta de la ficha");
            System.exit(2);
        }
        Path rutaFicha = Path.of(args[0]);

        String pedido = "";
        String cliente = "";
        String modelo = "";
        String diseno = "";
        Map<Integer, Integer> tallas = new TreeMap<>();
        int total = 0;

        try {
            //Lee el pedido por la entrada estándar
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            entrada.readLine(); //Salta la cabecera
            String linea;

            while ((linea = entrada.readLine()) != null) {
                if (linea.isBlank()) continue;
                String[] campos = linea.split(";", -1);

                //Los datos generales del pedido se toman de la primera fila
                if (pedido.isEmpty()) {
                    pedido = campos[0].trim();
                    cliente = campos[1].trim();
                    modelo = campos[2].trim();
                    diseno = campos[5].trim();
                }

                int talla = Integer.parseInt(campos[3].trim());
                int cantidad = Integer.parseInt(campos[4].trim());
                tallas.merge(talla, cantidad, Integer::sum);
                total += cantidad;
            }

        } catch (IOException | NumberFormatException | ArrayIndexOutOfBoundsException e) {
            System.err.println("ERROR: no se pudo procesar el pedido -> " + e.getMessage());
            System.exit(2);
        }

        //Contenido de la ficha que se entregará al taller
        List<String> ficha = new ArrayList<>();
        ficha.add("FICHA DE TALLER");
        ficha.add("Fecha: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")));
        ficha.add("Pedido: " + pedido);
        ficha.add("Cliente: " + cliente);
        ficha.add("Modelo: " + modelo);
        ficha.add("Diseño: " + diseno);
        ficha.add("");
        ficha.add("Talla | Pares");
        for (Map.Entry<Integer, Integer> t : tallas.entrySet()) {
            ficha.add(String.format("%5d | %5d", t.getKey(), t.getValue()));
        }
        ficha.add("TOTAL | " + String.format("%5d", total));

        try {
            Files.write(rutaFicha, ficha, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.err.println("ERROR: no se pudo guardar la ficha en " + rutaFicha);
            System.exit(2);
        }

        System.out.println("Ficha generada en " + rutaFicha);
        System.exit(0);
    }
}
