package psp; //La clase Validador está en el paquete psp.

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class Validador {

    public static void main(String[] args) {

        //Datos del pedido que envía el coordinador como argumentos, son obligatorios porque cambian en cada pedido
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
        } catch (NumberFormatException e) { //Si algún argumento no es un número es un fallo técnico
            System.err.println("ERROR: los argumentos deben ser números");
            System.exit(2);
        }

        //El total tiene que ser positivo y el rango de tallas no tiene sentido si la mínima es mayor que la máxima
        if (totalEsperado <= 0 || tallaMin > tallaMax) {
            System.err.println("ERROR: total o rango de tallas incorrecto");
            System.exit(2);
        }

        List<String> lineas = new ArrayList<>(); //Lista vacía donde se guardaran las líneas de los datos como texto

        try {
            //Lee la entrada línea a línea
            BufferedReader entrada = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
            String linea;
            //Lee una línea de datos y la guarda en "línea", cuando y no hay más líneas de datos acaba el bucle
            while ((linea = entrada.readLine()) != null) {
                lineas.add(linea);
            }

        } catch (IOException e) { //Gestiona un posible error al leer una entrada
            System.err.println("ERROR: no se pudo leer la entrada");
            System.exit(2);//Termina el proceso con el código 2, en referencia a un fallo técnico.
        }

        //Si no ha llegado ninguna línea el pedido no es válido y termina con el código 1
        if (lineas.isEmpty()) {
            System.err.println("ERROR: el pedido está vacío");
            System.exit(1);
        }

        //La primera línea debe ser la cabecera esperada, si no lo es las columnas no son fiables y se para aquí
        final String CABECERA_ESPERADA = "pedido;cliente;modelo;talla;cantidad;diseno";
        String cabecera = lineas.get(0).trim();

        if (!cabecera.equalsIgnoreCase(CABECERA_ESPERADA)) {
            System.err.println("ERROR: cabecera incorrecta: " + cabecera);
            System.exit(1);
        }

        List<String> errores = new ArrayList<>(); //Lista donde se acumulan todos los errores para mostrarlos juntos al final
        int totalPares = 0; //Suma de las cantidades válidas

        //Recorre las filas de datos empezando en 1 para saltar la cabecera
        for (int i = 1; i < lineas.size(); i++) {

            String fila = lineas.get(i).trim();
            int numLinea = i + 1; //Número de línea contando desde 1 para los mensajes de error

            //Las líneas vacías se ignoran, por ejemplo un salto de línea de más al final
            if (fila.isEmpty()) {
                continue;
            }

            //Separa la fila por cada ; y el -1 hace que se conserven los campos vacíos del final
            String[] campos = fila.split(";", -1);

            //Si no tiene 6 campos no se puede revisar el resto de la fila y se pasa a la siguiente
            if (campos.length != 6) {
                errores.add("Línea " + numLinea + ": tiene " + campos.length + " campos (se esperaban 6)");
                continue;
            }

            //Comprueba que ningún campo esté vacío
            for (int c = 0; c < campos.length; c++) {
                if (campos[c].trim().isEmpty()) {
                    errores.add("Línea " + numLinea + ": el campo " + (c + 1) + " está vacío");
                }
            }

            //La talla está en la posición 3 y debe ser un número dentro del rango
            try {
                int talla = Integer.parseInt(campos[3].trim());
                if (talla < tallaMin || talla > tallaMax) {
                    errores.add("Línea " + numLinea + ": talla " + talla + " fuera de rango (" + tallaMin + "-" + tallaMax + ")");
                }
            } catch (NumberFormatException e) { //parseInt lanza esta excepción si el texto no es un número
                errores.add("Línea " + numLinea + ": la talla no es un número -> " + campos[3]);
            }

            //La cantidad está en la posición 4, debe ser mayor que 0 y si es válida se suma al total
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

        //La suma de pares tiene que coincidir con el total esperado del pedido
        if (totalPares != totalEsperado) {
            errores.add("El total de pares es " + totalPares + " y se esperaban " + totalEsperado);
        }

        //Resultado final, el código de salida es lo que leerá el coordinador para saber si el pedido es válido
        if (errores.isEmpty()) {
            System.out.println("VALIDO: pedido correcto con " + totalPares + " pares");
            System.exit(0); //Termina con el código 0, el pedido es válido
        } else {
            System.out.println("NO VALIDO: " + errores.size() + " errores encontrados");
            //Los errores se envían por la salida de error para separarlos del resultado
            for (String error : errores) {
                System.err.println(error);
            }
            System.exit(1); //Termina con el código 1, el pedido no es válido
        }
    }
}