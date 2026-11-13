package psp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class Validador {

    public static void main(String[] args) {

        if (args.length != 3) {
            System.err.println("ERROR: se esperaban 3 argumentos <total_pares> <talla_min> <talla_max>");
            System.exit(2);
        }

        int totalEsperado = 0;
        int tallaMin = 0;
        int tallaMax = 0;

        try {
            totalEsperado = Integer.parseInt(args[0]);
            tallaMin = Integer.parseInt(args[1]);
            tallaMax = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            System.err.println("ERROR: los argumentos deben ser números");
            System.exit(2);
        }

        if (totalEsperado <= 0 || tallaMin > tallaMax) {
            System.err.println("ERROR: total o rango de tallas incorrecto");
            System.exit(2);
        }

        List<String> lineas = new ArrayList<>();

        try {
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            String linea;
            while ((linea = entrada.readLine()) != null) {
                lineas.add(linea);
            }

        } catch (IOException e) {
            System.err.println("ERROR: no se pudo leer la entrada");
            System.exit(2);
        }

        if (lineas.isEmpty()) {
            System.err.println("ERROR: el pedido está vacío");
            System.exit(1);
        }

        final String CABECERA_ESPERADA = "pedido;cliente;modelo;talla;cantidad;diseno";
        String cabecera = lineas.get(0).trim();

        if (!cabecera.equalsIgnoreCase(CABECERA_ESPERADA)) {
            System.err.println("ERROR: cabecera incorrecta: " + cabecera);
            System.exit(1);
        }

        List<String> errores = new ArrayList<>();
        int totalPares = 0;

        for (int i = 1; i < lineas.size(); i++) {

            String fila = lineas.get(i).trim();
            int numLinea = i + 1;

            if (fila.isEmpty()) {
                continue;
            }

            String[] campos = fila.split(";", -1);

            if (campos.length != 6) {
                errores.add("Línea " + numLinea + ": tiene " + campos.length + " campos (se esperaban 6)");
                continue;
            }

            for (int c = 0; c < campos.length; c++) {
                if (campos[c].trim().isEmpty()) {
                    errores.add("Línea " + numLinea + ": el campo " + (c + 1) + " está vacío");
                }
            }

            try {
                int talla = Integer.parseInt(campos[3].trim());
                if (talla < tallaMin || talla > tallaMax) {
                    errores.add("Línea " + numLinea + ": talla " + talla + " fuera de rango (" + tallaMin + "-" + tallaMax + ")");
                }
            } catch (NumberFormatException e) {
                errores.add("Línea " + numLinea + ": la talla no es un número -> " + campos[3]);
            }

            try {
                int cantidad = Integer.parseInt(campos[4].trim());
                if (cantidad <= 0) {
                    errores.add("Línea " + numLinea + ": la cantidad debe ser mayor que 0 -> " + cantidad);
                } else {
                    totalPares += cantidad;
                }
            } catch (NumberFormatException e) {
                errores.add("Línea " + numLinea + ": la cantidad no es un número -> " + campos[4]);
            }
        }

        if (totalPares != totalEsperado) {
            errores.add("El total de pares es " + totalPares + " y se esperaban " + totalEsperado);
        }

        if (errores.isEmpty()) {
            System.out.println("VALIDO: pedido correcto con " + totalPares + " pares");
            System.exit(0);
        } else {
            System.out.println("NO VALIDO: " + errores.size() + " errores encontrados");
            for (String error : errores) {
                System.err.println(error);
            }
            System.exit(1);
        }
    }
}