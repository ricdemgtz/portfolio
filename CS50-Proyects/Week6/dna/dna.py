import csv
import sys


def main():
    """
    Identifies a person based on their DNA sequence by comparing STR counts
    with a database.
    """

    # Check for correct number of command-line arguments
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py data.csv sequence.txt")

    # --- Read Database File ---
    database = []
    # Open the CSV file provided as the first command-line argument
    with open(sys.argv[1], "r") as file:
        reader = csv.DictReader(file)
        # The first row contains STR names, get them from fieldnames
        # The first fieldname is 'name', so we slice from the second element
        str_sequences = reader.fieldnames[1:]
        # Read all people's data into the database list
        for row in reader:
            database.append(row)

    # --- Read DNA Sequence File ---
    # Open the text file provided as the second command-line argument
    with open(sys.argv[2], "r") as file:
        sequence = file.read()

    # --- Find Longest Match for Each STR ---
    # This dictionary will store the results for the given sequence
    final_counts = {}
    # For each STR, compute the longest run in the sequence
    for subsequence in str_sequences:
        final_counts[subsequence] = longest_match(sequence, subsequence)

    # --- Compare with Database ---
    # Iterate through each person in the database
    for person in database:
        match_count = 0
        # Check if all STR counts match for the current person
        for subsequence in str_sequences:
            # Convert the STR count from the database (string) to an integer for comparison
            if int(person[subsequence]) == final_counts[subsequence]:
                match_count += 1

        # If all STRs match, we found our person
        if match_count == len(str_sequences):
            print(person["name"])
            return  # Exit the program after finding a match

    # If the loop finishes without finding a match for any person
    print("No match")


def longest_match(sequence, subsequence):
    """Returns the length of the longest run of a subsequence in a sequence."""

    # Initialize variables
    longest_run = 0
    sub_len = len(subsequence)
    seq_len = len(sequence)

    # Iterate through the sequence to find the longest consecutive run
    for i in range(seq_len):
        # Initialize a counter for the current run
        current_run = 0
        # Check for consecutive matches starting from position i
        while True:
            start = i + current_run * sub_len
            end = start + sub_len
            # If the slice of the sequence matches the subsequence
            if sequence[start:end] == subsequence:
                current_run += 1
            # If it doesn't match, break the inner loop
            else:
                break
        # Update the longest run found so far
        longest_run = max(longest_run, current_run)

    return longest_run


# Call the main function to run the program
if __name__ == "__main__":
    main()



