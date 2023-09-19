from bs4 import BeautifulSoup
import json
import os
import re

def extract_first_verse(text):
    match = re.search(r'\d+([A-Z].*?)(?=\d+[A-Z]|$)', text)
    if match:
        verse_text = match.group(1).strip()
        return verse_text
    else:
        return None


def HTM_To_Json(book_name, book_number):
    directory_name = 'books'
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    if len(str(book_number)) == 1:
        book_number = '0' + str(book_number)
    book_number = str(book_number)

    path = f'Bible_English_AMPC\Bible_English_AMPC\{book_number}_{book_name}.htm'
    with open(fr"{path}", 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    book = book_name
    chapter = None

    data = {}

    for tag in soup.find_all(['h4', 'p']):
        if tag.name == 'h4':
            chapter = tag.get_text()
            if book not in data:
                data[book] = {}
        elif tag.name == 'p':
            verse_number = tag.sup.get_text() if tag.sup else None

            verse_text = tag.get_text(strip=True)

            first_verse = extract_first_verse(verse_text)

            if verse_number and first_verse:
                if chapter not in data[book]:
                    data[book][chapter] = []  
                data[book][chapter].append({
                    'verse_number': verse_number,
                    'verse_text': first_verse 
                })

    with open(fr'books/book{book_number}.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"Data has been organized by book, chapter, and verse, and saved to 'book{book_number}.json'.")

if __name__ == "__main__":
    print("Starting...")

    folder_path = r"Bible_English_AMPC\Bible_English_AMPC"

    files = os.listdir(folder_path)

    for file_name in files:
        if os.path.isfile(os.path.join(folder_path, file_name)):
            try:
                parts = file_name.split('_')
                idx = int(parts[0])
                book = parts[1].split('.')[0]
                print(f"Currently on Book {idx} of {len(files)}")
                HTM_To_Json(book.lower(), idx)
            except Exception as e:
                print(e)
                print(f"Error on Book {idx} of {len(files)}")
                continue
        #exit()

    print("Done!")
