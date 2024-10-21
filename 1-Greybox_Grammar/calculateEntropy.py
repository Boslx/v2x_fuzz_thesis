import argparse
import os
from scipy.stats import entropy


def calculate_combined_entropy(folder_path):
    all_bytes = bytearray()

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file and read it in binary modea
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                all_bytes.extend(file.read())

    # Calculate entropy using scipy
    return entropy(all_bytes, base=8)


def main():
    parser = argparse.ArgumentParser(description='Calculate combined entropy of binary files in a folder.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing binary files')
    args = parser.parse_args()

    if not os.path.isdir(args.folder_path):
        print(f"Error: '{args.folder_path}' is not a valid directory.")
        return

    combined_entropy = calculate_combined_entropy(args.folder_path)
    print(f"Combined entropy of binary files in '{args.folder_path}': {combined_entropy}")


if __name__ == "__main__":
    main()
