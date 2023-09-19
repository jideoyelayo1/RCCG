import json
import xml.etree.ElementTree as ET


def json_to_xml(data):
    root = ET.Element("XMLBIBLE", attrib={"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "biblename": "ENGLISHAMP"})

    for book_name, chapters in data.items():
        book_element = ET.SubElement(root, "BIBLEBOOK", attrib={"bname": book_name})

        for chapter_name, verses in chapters.items():
            chapter_element = ET.SubElement(book_element, "CHAPTER", attrib={"cnumber": chapter_name})
            
            for verse in verses:
                verse_element = ET.SubElement(chapter_element, "VERS", attrib={"vnumber": verse["verse_number"]})
                verse_element.text = verse["verse_text"]
                
        print(book_name + " has been added to the XML file.")

    xml_str = ET.tostring(root, encoding="UTF-8", method="xml").decode()
    

    xml_lines = xml_str.split('>')
    formatted_xml = '>\n'.join(xml_lines)
    
    return formatted_xml


json_data = {}
for book_number in range(1, 67): # 66 books in the Bible
    try:
        with open(f'books/book{str(book_number).zfill(2)}.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            json_data.update(data)
    except Exception as e:
        print(e)
        print(f"Error on Book number: {book_number}")
        continue


xml_content = json_to_xml(json_data)


with open("bible_AMPC.xml", "w", encoding="utf-8") as xml_file:
    xml_file.write(xml_content)

print("XML file 'bible_AMPC.xml' has been created.")
