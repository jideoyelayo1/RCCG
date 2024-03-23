import xml.etree.ElementTree as ET
import json

def count_verses(xml_file):
    result = []

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for book in root.findall(".//BIBLEBOOK"):
        book_name = book.get("bname")
        book_info = {"book": book_name, "chapters": []}

        for chapter in book.findall(".//CHAPTER"):
            chapter_number = chapter.get("cnumber")
            verse_count = len(chapter.findall(".//VERS"))

            chapter_info = {"chapter": chapter_number, "verses": verse_count}
            book_info["chapters"].append(chapter_info)

        result.append(book_info)

    return result

def save_to_json(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    xml_file_path = "bible_AMP.xml"
    json_file_path = "bible.json"

    data = count_verses(xml_file_path)
    save_to_json(data, json_file_path)

    print(f"Data saved to {json_file_path}")
