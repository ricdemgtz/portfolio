#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool is_valid_key(string key_str);
char encrypt_char(char plain_char, int key);

int main(int argc, string argv[])
{
    // Check for exactly one command-line argument
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // Validate that the key contains only digits
    if (!is_valid_key(argv[1]))
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // Convert key from string to integer
    int key = atoi(argv[1]);

    // Get plaintext input from user
    string plaintext = get_string("plaintext: ");

    // Prepare to print encrypted text
    printf("ciphertext: ");

    // Encrypt each character and print result
    int text_length = strlen(plaintext);
    for (int i = 0; i < text_length; i++)
    {
        char cipher_char = encrypt_char(plaintext[i], key);
        printf("%c", cipher_char);
    }
    printf("\n");

    return 0;
}

// Checks if key string contains only numeric digits
bool is_valid_key(string key_str)
{
    int key_length = strlen(key_str);
    for (int i = 0; i < key_length; i++)
    {
        if (!isdigit(key_str[i]))
        {
            return false;
        }
    }
    return true;
}

// Encrypts a single character using Caesar cipher
char encrypt_char(char plain_char, int key)
{
    if (isalpha(plain_char))
    {
        // Determine base ASCII value for upper/lowercase
        char base = isupper(plain_char) ? 'A' : 'a';

        // Calculate shifted position within alphabet
        int shifted_position = (plain_char - base + key) % 26;

        // Handle wrap-around for negative values (though key is non-negative)
        if (shifted_position < 0)
        {
            shifted_position += 26;
        }

        return base + shifted_position;
    }

    // Return non-alphabetic characters unchanged
    return plain_char;
}
