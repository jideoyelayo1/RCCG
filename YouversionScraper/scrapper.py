from bs4 import BeautifulSoup
import requests
import json
import os
import re
import csv
import json
import xml.etree.ElementTree as ET
import time


def convert_text_to_json(book_name, chapter, text, json_data):
    verses = text.split('\n')

    if book_name not in json_data:
        json_data[book_name] = {}

    if chapter not in json_data[book_name]:
        json_data[book_name][chapter] = []

    for verse in verses:
        verse_match = re.match(r'(\d+):\s(.+)', verse)
        if verse_match:
            verse_number, verse_text = verse_match.groups()
            verse_text = ' '.join(verse_text.split())
            json_data[book_name][chapter].append({
                "verse_number": verse_number,
                "verse_text": verse_text
            })


def webScrapToJSON(book_name, chapterLength, book_code, bookNumber, version):
    json_data = {}
    code = 1849
    if version == "TPT":
        code = 1849
    if version == "AMPC":
        code = 8
    if version == "AMP":
        code = 1588
    if version == "ASV":
        code = 12
    if version == "CEB":
        code = 1849
    if version == "ERV":
        code = 1849
    if version == "GNBDC":
        code = 416
    if version == "GNT":
        code = 68
    if version == "NET":
        code = 107

    for chapter in range(1, chapterLength + 1):
        webpage = f"https://www.bible.com/bible/{code}/{book_code}.{chapter}.{version}"
        page_to_scrape = requests.get(webpage)
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        verse_elements = soup.select('span.ChapterContent_content__RrUqA')

        current_verse_number = None
        verses_text = ""

        for verse_element in verse_elements:
            verse_number_span = verse_element.find_previous(
                'span', class_='ChapterContent_verse__57FIw')
            if verse_number_span:
                verse_number = verse_number_span.find(
                    'span', class_='ChapterContent_label__R2PLt')
                if verse_number:
                    verse_number = verse_number.get_text()
                else:
                    verse_number = "Unknown"

                verse_text = verse_element.get_text().strip()
                verse_text = re.sub(r'^(Unknown|#):', '', verse_text)
                verses_text += f"{verse_number}: {verse_text}\n"

        processed_text = ""
        for line in verses_text.splitlines():
            if re.match(r'^(Unknown|#):', line):
                line = re.sub(r'^(Unknown|#):', '', line)
                if processed_text:
                    processed_text = processed_text.rstrip("\n")
                    processed_text += " " + line
            else:
                if processed_text:
                    processed_text += "\n"
                processed_text += line
        convert_text_to_json(book_name, str(chapter),
                             processed_text, json_data)
    bookId = str(bookNumber) if len(
        str(bookNumber)) == 2 else '0' + str(bookNumber)

    if not os.path.exists(f"{version}_tmpfolder"):
        os.makedirs(f"{version}_tmpfolder")
        print(f"Folder '{version}_tmpfolder' created.")

    with open(f"{version}_tmpfolder/book{bookId}.json", 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


def Load_cvs():
    res = []
    with open('biblebooks.csv') as file:
        csv_reader = csv.reader(file)
        rowCnt = 0
        for row in csv_reader:
            if rowCnt == 0:
                rowCnt += 1
                continue
            bookname = row[0].strip()
            chapterLength = row[1].strip()
            biblecode = row[2].strip()
            if biblecode == "N/A":
                res.append(None)
                continue
            res.append((bookname, chapterLength, biblecode))
            rowCnt += 1

    if len(res) == 0:
        print("Error with loading CSV")
    return res


def formatBookName(s):
    if not s[0].isdigit():
        return s[0].upper() + s[1:]
    else:
        return s[0] + " " + s[1].upper() + s[2:]


def json_to_xml(data, version):
    root = ET.Element("XMLBIBLE", attrib={
                      "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "biblename": f"ENGLISH_{version}"})

    for book_name, chapters in data.items():
        book_element = ET.SubElement(root, "BIBLEBOOK", attrib={
                                     "bname": formatBookName(book_name)})

        for chapter_name, verses in chapters.items():
            chapter_element = ET.SubElement(book_element, "CHAPTER", attrib={
                                            "cnumber": chapter_name})

            for verse in verses:
                verse_element = ET.SubElement(chapter_element, "VERS", attrib={
                                              "vnumber": verse["verse_number"]})
                verse_element.text = verse["verse_text"]

        print(book_name + " has been added to the XML file.")

    xml_str = ET.tostring(root, encoding="UTF-8", method="xml").decode()

    xml_lines = xml_str.split('>')
    formatted_xml = '>'.join(xml_lines)

    return formatted_xml


def webScrap(version):
    print("Starting Scrapping...")

    datas = Load_cvs()
    currBookNo = 1
    for data in datas:
        if data is None:
            currBookNo += 1
            continue
        webScrapToJSON(data[0], int(data[1]), data[2], currBookNo, version)
        print(f"Book number {currBookNo} loaded")
        currBookNo += 1

    print("Done Scrapping!")


def JSON_merger(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    merged_data = {}
    for book, chapters in data.items():
        merged_data[book] = {}
        for chapter, verses in chapters.items():
            merged_data[book][chapter] = []
            verse_dict = {}
            for verse in verses:
                verse_number = verse["verse_number"]
                verse_text = verse["verse_text"]
                if verse_number not in verse_dict:
                    verse_dict[verse_number] = verse_text
                else:
                    verse_dict[verse_number] += " " + verse_text
            merged_verses = [{"verse_number": num, "verse_text": text}
                             for num, text in verse_dict.items()]
            merged_data[book][chapter] = merged_verses

    with open(filename, 'w') as output_file:
        json.dump(merged_data, output_file, indent=4)


def JsonToXML(version):
    print("Starting Loading...")
    folderlocation = f"{version}_tmpfolder"
    json_data = {}
    for book_number in range(1, 67):  # 66 books in the Bible
        if is_page_empty(f'{folderlocation}/book{str(book_number).zfill(2)}.json'):
            continue
        try:
            filename = f'{folderlocation}/book{str(book_number).zfill(2)}.json'
            if version != "TPT" and version != "GNT":
                JSON_merger(filename)
            with open(f'{folderlocation}/book{str(book_number).zfill(2)}.json', 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                json_data.update(data)
        except Exception as e:
            print(e)
            print(f"Error on Book number: {book_number}")
            continue

    xml_content = json_to_xml(json_data, version)

    with open(f"bible_{version}.xml", "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_content)

    print(f"XML file 'bible_{version}.xml' has been created.")


def is_page_empty(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for chapter in data.values():
            if "[]" in str(chapter):
                return True
        return False
    except (FileNotFoundError, json.JSONDecodeError):
        return True


def postProcess(version):
    tree = ET.parse(f'bible_{version}.xml')
    root = tree.getroot()

    def remove_brackets_and_single_letter(text):
        result = []
        inside_brackets = False

        for char in text:
            if char == '(':
                inside_brackets = True
            elif char == ')':
                inside_brackets = False
            elif not inside_brackets:
                result.append(char)

        return ''.join(result)

    for element in root.iter():
        if element.text:
            element.text = remove_brackets_and_single_letter(element.text)

    tree.write(f'bible_{version}.xml')


if __name__ == "__main__":
    # Enter what version for the website Youversion You want to turn into an XML

    # version = "TPT"
    version = str(input("What version do you want? "))
    print(f"Getting {version} and turning it into an XML")
    start_time = time.time()

    webScrap(version)
    JsonToXML(version)
    # postProcess(version) ### doesnt work / not needed

    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f"Program took: {elapsed_time} seconds( {elapsed_time//60} mins)")
