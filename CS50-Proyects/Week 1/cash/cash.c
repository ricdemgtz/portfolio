#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Prompt the user for change owed, in cents
    int cents;
    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);

    int coins = 0;

    // Calculate the number of coins to give back
    while (cents > 0) // Continue until all cents are given back
    {
        // Calculate how many quarters you should give customer
        // Subtract the value of those quarters from cents
        if (cents >= 25)
        {
            cents -= 25; // Use shorthand for subtraction
            coins++;
        }
        // Calculate how many dimes you should give customer
        // Subtract the value of those dimes from remaining cents
        else if (cents >= 10)
        {
            cents -= 10;
            coins++;
        }
        // Calculate how many nickels you should give customer
        // Subtract the value of those nickels from remaining cents
        else if (cents >= 5)
        {
            cents -= 5;
            coins++;
        }
        // Calculate how many pennies you should give customer
        // Subtract the value of those pennies from remaining cents
        else if (cents >= 1)
        {
            cents -= 1;
            coins++;
        }
    }

    // Print the total number of coins used
    printf("%i\n", coins);
}
