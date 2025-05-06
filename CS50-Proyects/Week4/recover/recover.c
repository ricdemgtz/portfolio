#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BLOCK_SIZE 512
#define JPEG_START_SIZE 4

// Función para verificar si un bloque comienza con un header JPEG
bool is_jpeg_start(const uint8_t *buffer)
{
    if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff)
    {
        uint8_t fourth_byte = buffer[3];
        return (fourth_byte >= 0xe0 && fourth_byte <= 0xef);
    }
    return false;
}

int main(int argc, char *argv[])
{
    // 1. Verificar el número de argumentos
    if (argc != 2)
    {
        fprintf(stderr, "Uso: %s archivo_memoria\n", argv[0]);
        return 1;
    }

    // 2. Abrir el archivo de la tarjeta de memoria
    FILE *infile = fopen(argv[1], "rb");
    if (infile == NULL)
    {
        fprintf(stderr, "No se pudo abrir el archivo: %s\n", argv[1]);
        return 1;
    }

    // Buffer para leer bloques de la tarjeta de memoria
    uint8_t buffer[BLOCK_SIZE];
    size_t bytes_read;
    int file_count = 0;
    FILE *outfile = NULL;
    char filename[12]; // ###.jpg\0 (suficiente espacio)

    // 3. Leer datos de la tarjeta de memoria en bloques de 512 bytes
    while ((bytes_read = fread(buffer, 1, BLOCK_SIZE, infile)) == BLOCK_SIZE)
    {
        // 4. Buscar el inicio de un archivo JPEG
        if (is_jpeg_start(buffer))
        {
            // Si ya estábamos escribiendo un archivo, cerrarlo
            if (outfile != NULL)
            {
                fclose(outfile);
            }

            // Crear un nuevo nombre de archivo ###.jpg
            sprintf(filename, "%03d.jpg", file_count++);

            // Abrir un nuevo archivo para escritura
            outfile = fopen(filename, "wb");
            if (outfile == NULL)
            {
                fprintf(stderr, "No se pudo crear el archivo: %s\n", filename);
                fclose(infile);
                return 1;
            }

            // Escribir el bloque actual al nuevo archivo JPEG
            fwrite(buffer, 1, bytes_read, outfile);
        }
        else if (outfile != NULL)
        {
            // Si ya encontramos un JPEG, seguir escribiendo bloques
            fwrite(buffer, 1, bytes_read, outfile);
        }
    }

    // 5. Cerrar cualquier archivo restante
    if (outfile != NULL)
    {
        fclose(outfile);
    }

    // 6. Cerrar el archivo de la tarjeta de memoria
    fclose(infile);

    return 0;
}
