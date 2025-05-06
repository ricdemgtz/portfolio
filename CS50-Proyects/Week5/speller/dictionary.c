// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// Let's be a bit more generous with the number of buckets to minimize collisions.
// A prime number often helps with better distribution.
const unsigned int HASH_TABLE_SIZE = 5003; // A reasonably sized prime number

// Hash table
node *hash_table[HASH_TABLE_SIZE];

// Keep track of the number of words loaded in the dictionary
unsigned int word_count = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // Let's make this case-insensitive. First, create a lowercase version of the word.
    int len = strlen(word);
    char lower_word[len + 1];
    for (int i = 0; i < len; i++)
    {
        lower_word[i] = tolower(word[i]);
    }
    lower_word[len] = '\0';

    // Calculate the hash value for the lowercase word.
    unsigned int hash_value = hash(lower_word);

    node *current = hash_table[hash_value];
    while (current != NULL)
    {
        if (strcmp(current->word, lower_word) == 0)
        {
            return true; // Word found!
        }
        current = current->next;
    }

    return false; // Word not found in the dictionary.
}

// Hashes word to a number.
unsigned int hash(const char *word)
{
    unsigned long hash = 5381;
    int c;

    while ((c = *word++))
    {
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    }

    return hash % HASH_TABLE_SIZE;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Open the dictionary file. If we can't, something's wrong.
    FILE *dict_file = fopen(dictionary, "r");
    if (dict_file == NULL)
    {
        return false;
    }

    char buffer[LENGTH + 1];
    // Read the dictionary word by word.
    while (fscanf(dict_file, "%s", buffer) != EOF)
    {
        // Allocate memory for a new node. If we can't, we're in trouble.
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            fclose(dict_file);
            unload(); // Clean up any memory we might have already allocated.
            return false;
        }

        // Copy the word into the new node.
        strcpy(new_node->word, buffer);
        new_node->next = NULL;

        // Calculate the hash value for this word.
        unsigned int hash_value = hash(buffer);

        // Insert the new node at the beginning of the linked list at the hash index.
        new_node->next = hash_table[hash_value];
        hash_table[hash_value] = new_node;

        // Increment the word count.
        word_count++;
    }

    // We've successfully loaded all words. Close the file.
    fclose(dict_file);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // Iterate through each bucket in the hash table.
    for (int i = 0; i < HASH_TABLE_SIZE; i++)
    {
        node *current = hash_table[i];
        // Traverse the linked list and free each node.
        while (current != NULL)
        {
            node *temp = current;
            current = current->next;
            free(temp);
        }
        hash_table[i] = NULL; // Ensure the pointer in the table is also reset.
    }
    word_count = 0; // Reset the word count.
    return true;
}
