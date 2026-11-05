package psp; //La clase ResumenTallas está en el paquete psp.

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.TreeMap;

public class ResumenTallas {

    public static void main(String[] args) {

        Map<Integer, Integer> tallas = new TreeMap<>(); //TreeMap guarda las tallas ordenadas de menor a mayor con su cantidad
        int total = 0;

        try {
            //Lee el pedido por la entrada estándar
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            entrada.readLine(); //Salta la cabecera
            String linea;

            while ((linea = entrada.readLine()) != null) {
                if (linea.isBlank()) continue;
                String[] campos = linea.split(";", -1);
                int talla = Integer.parseInt(campos[3].trim());
                int cantidad = Integer.parseInt(campos[4].trim());
                tallas.merge(talla, cantidad, Integer::sum); //Si la talla ya existe suma la cantidad, si no la añade
                total += cantidad;
            }

        } catch (IOException | NumberFormatException | ArrayIndexOutOfBoundsException e) {
            //El pedido llega ya validado, si aun así falla es un fallo técnico
            System.err.println("ERROR: no se pudo procesar el pedido -> " + e.getMessage());
            System.exit(2);
        }

        //Muestra una línea por talla y el total, el coordinador lo recoge por la salida estándar
        for (Map.Entry<Integer, Integer> t : tallas.entrySet()) {
            System.out.println("Talla " + t.getKey() + " -> " + t.getValue() + " pares");
        }
        System.out.println("TOTAL -> " + total + " pares");
        System.exit(0);
    }
}