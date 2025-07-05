from cs50 import get_int


def generate_pyramids(high):
    for i in range(1, high + 1):
        spaces_left = " " * (high - i)
        hashes_left = "#" * i
        separation = "  "
        hashes_right = "#" * i
        print(f"{spaces_left}{hashes_left}{separation}{hashes_right}")


while True:
    try:
        high = get_int("Prompt the high of the pyramids between 1 & 8: ")
        if 1 <= high <= 8:
            generate_pyramids(high)
            break
        else:
            print("The high must be a number between 1 and 8")

    except ValueError:
        print("Input wrong, Please prompt a positive integer")
