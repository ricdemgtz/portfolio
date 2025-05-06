#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Number of bytes in .wav header
const int HEADER_SIZE = 44;

// Helper function to handle file errors
void handle_file_error(FILE *file, const char *filename, const char *mode)
{
    if (file == NULL)
    {
        printf("Could not open file '%s' in mode '%s'.\n", filename, mode);
        exit(1);
    }
}

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 4)
    {
        printf("Usage: ./volume input.wav output.wav factor\n");
        return 1;
    }

    // Open input file
    FILE *input = fopen(argv[1], "r");
    handle_file_error(input, argv[1], "r");

    // Open output file
    FILE *output = fopen(argv[2], "w");
    if (output == NULL)
    {
        // Close input file before exiting
        fclose(input);
        handle_file_error(output, argv[2], "w");
    }

    // Parse and validate scaling factor
    float factor = atof(argv[3]);
    if (factor < 0)
    {
        printf("Error: Factor must be a positive number.\n");
        fclose(input);
        fclose(output);
        return 1;
    }
    if (factor == 0)
    {
        printf("Warning: Factor is zero. The output audio will be silent.\n");
    }

    // Copy header from input file to output file
    uint8_t header[HEADER_SIZE];
    if (fread(header, HEADER_SIZE, 1, input) != 1)
    {
        printf("Error: Could not read header from input file.\n");
        fclose(input);
        fclose(output);
        return 1;
    }
    if (fwrite(header, HEADER_SIZE, 1, output) != 1)
    {
        printf("Error: Could not write header to output file.\n");
        fclose(input);
        fclose(output);
        return 1;
    }

    // Read samples from input file and write updated data to output file
    int16_t buffer;
    while (fread(&buffer, sizeof(int16_t), 1, input) == 1)
    {
        // Update volume of sample
        buffer = (int16_t) (buffer * factor);

        // Write updated sample to output file
        if (fwrite(&buffer, sizeof(int16_t), 1, output) != 1)
        {
            printf("Error: Could not write sample to output file.\n");
            fclose(input);
            fclose(output);
            return 1;
        }
    }

    // Check if the loop ended due to an error
    if (!feof(input))
    {
        printf("Error: Failed to read samples from input file.\n");
        fclose(input);
        fclose(output);
        return 1;
    }

    // Close files
    fclose(input);
    fclose(output);

    printf("Volume adjustment completed successfully.\n");
    return 0;
}
