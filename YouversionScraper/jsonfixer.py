import json
import os

# Define the directory where your JSON files are located
json_directory = "AMP_tmpfolder"

def consolidate_verses(book_data):
    # Create a dictionary to store consolidated verses for a specific book
    consolidated_data = {}

    # Iterate through each book
    for book_name, verse_dict in book_data.items():
        # Create a dictionary to store consolidated verses within the book
        consolidated_book = {}

        # Iterate through the verse numbers as strings
        for verse_number_str, verse_objects in verse_dict.items():
            # Create a list to store consolidated verses within the chapter
            consolidated_chapter = []

            # Iterate through the verse objects (usually just one)
            for verse_object in verse_objects:
                verse_text = verse_object["verse_text"]

                # Add the verse to the list of consolidated verses within the chapter
                consolidated_chapter.append({
                    "verse_number": verse_number_str,
                    "verse_text": verse_text
                })

            # Store the consolidated chapter in the book's dictionary
            consolidated_book[verse_number_str] = consolidated_chapter

        # Store the consolidated book in the final dictionary
        consolidated_data[book_name] = consolidated_book

    return consolidated_data

# Loop through the JSON files in the directory
for filename in os.listdir(json_directory):
    if filename.endswith(".json"):
        file_path = os.path.join(json_directory, filename)

        # Open and load the JSON file with explicit encoding
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Update the JSON data using the consolidation function
        consolidated_data = consolidate_verses(data)

        # Overwrite the original JSON file with the updated data
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(consolidated_data, json_file, indent=4, ensure_ascii=False)

        print(f"Updated: {filename}")

print("All JSON files updated.")
