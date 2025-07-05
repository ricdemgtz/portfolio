from cs50 import get_string


def obtener_numero_tarjeta():
    """Prompts the user for a credit card number using CS50's get_string."""
    while True:
        try:
            numero_str = get_string("Number: ")
            if numero_str is not None and numero_str.isdigit():
                return numero_str
            else:
                print("Invalid input. Please enter only numbers.")
        except KeyboardInterrupt:
            respuesta = input("\nAre you sure you want to exit? (yes/no): ").lower()
            if respuesta == 'yes':
                print("Exiting program.")
                return None
            else:
                print("Continuing...")
                continue


def es_valida_luhn(numero_str):
    """Checks if a credit card number (string) is valid according to the Luhn algorithm."""
    digits = [int(digit) for digit in numero_str]
    total_sum = 0
    number_length = len(digits)

    # Sum the digits that are not multiplied (starting from the last one)
    for i in range(number_length - 1, -1, -2):
        total_sum += digits[i]

    # Multiply every second digit by 2 (starting from the second-to-last) and sum their digits
    for i in range(number_length - 2, -1, -2):
        product = digits[i] * 2
        total_sum += product - 9 if product > 9 else product

    return total_sum % 10 == 0


def identificar_tarjeta(numero_str):
    """Identifies the type of credit card based on the number (string)."""
    length = len(numero_str)
    if length == 15 and (numero_str.startswith('34') or numero_str.startswith('37')):
        return "AMEX"
    elif length == 16 and numero_str.startswith(('51', '52', '53', '54', '55')):
        return "MASTERCARD"
    elif (length == 13 or length == 16) and numero_str.startswith('4'):
        return "VISA"
    else:
        return "INVALID"


def procesar_tarjeta():
    """Main function to get, validate, and identify the credit card."""
    card_number = obtener_numero_tarjeta()

    if card_number is not None:
        if es_valida_luhn(card_number):
            card_type = identificar_tarjeta(card_number)
            print(card_type)
        else:
            print("INVALID")
    else:
        pass


if __name__ == "__main__":
    procesar_tarjeta()
