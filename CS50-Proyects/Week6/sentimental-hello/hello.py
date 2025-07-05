def say_hello(name):
    """Saluda a la persona con el nombre proporcionado."""
    print(f"Hello, {name}!")


def is_valid_name(name):
    """Verifica si la entrada es un nombre válido (no vacío ni solo espacios)."""
    return name.strip() != ""


while True:
    try:
        name = input("What is your name?: ")
        if is_valid_name(name):
            say_hello(name)
            break
        else:
            print("Please enter a valid name.")
    except Exception as e:
        print(f"An error occurred: {e}. Please try again.")
