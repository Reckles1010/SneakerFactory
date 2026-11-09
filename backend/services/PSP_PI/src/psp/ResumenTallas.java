package psp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.TreeMap;

public class ResumenTallas {

    public static void main(String[] args) {

        Map<Integer, Integer> tallas = new TreeMap<>();
        int total = 0;

        try {
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            entrada.readLine();
            String linea;

            while ((linea = entrada.readLine()) != null) {
                if (linea.isBlank()) continue;
                String[] campos = linea.split(";", -1);
                int talla = Integer.parseInt(campos[3].trim());
                int cantidad = Integer.parseInt(campos[4].trim());
                tallas.merge(talla, cantidad, Integer::sum);
                total += cantidad;
            }

        } catch (IOException | NumberFormatException | ArrayIndexOutOfBoundsException e) {
            System.err.println("ERROR: no se pudo procesar el pedido -> " + e.getMessage());
            System.exit(2);
        }

        for (Map.Entry<Integer, Integer> t : tallas.entrySet()) {
            System.out.println("Talla " + t.getKey() + " -> " + t.getValue() + " pares");
        }
        System.out.println("TOTAL -> " + total + " pares");
        System.exit(0);
    }
}