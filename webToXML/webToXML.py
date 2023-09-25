from bs4 import BeautifulSoup
import requests
import json
import os
import csv
import json
import xml.etree.ElementTree as ET


def webScrapToJSON(bookName, chapterLength, bookNumber, version="AMPC"):
    verses_dict = {
        f"{bookName}": {}
    }

    for chapter in range(1, chapterLength + 1):
        webpage = f"https://www.biblegateway.com/passage/?search={bookName}%20{chapter}&version={version}"
        page_to_scrape = requests.get(webpage)
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        chapter_verses = []

        verse_elements = soup.find_all('p', class_='verse')

        for index, verse_element in enumerate(verse_elements):
            verse_number_element = verse_element.find('sup', class_='versenum')
            if verse_number_element:
                verse_number = verse_number_element.text.strip()
            else:
                verse_number = str(index + 1)

            verse_text_element = verse_element.find('span', class_='text')
            if verse_text_element:
                verse_text = verse_text_element.text.replace(
                    verse_number, '').strip()
            else:
                verse_text = "N/A"

            verse_data = {
                "verse_number": verse_number,
                "verse_text": verse_text
            }

            chapter_verses.append(verse_data)

        verses_dict[bookName][str(chapter)] = chapter_verses

    bookId = str(bookNumber) if len(
        str(bookNumber)) > 9 else "0" + str(bookNumber)
    if not os.path.exists(f"{version}_tmpfolder"):
        os.makedirs(f"{version}_tmpfolder")
        print(f"Folder '{version}_tmpfolder' created.")

    with open(f'{version}_tmpfolder/book{bookId}.json', 'w', encoding='utf-8') as json_file:
        json.dump(verses_dict, json_file, ensure_ascii=False, indent=4)

    print(f"JSON file 'book{bookId}.json' created successfully.")


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
            res.append((bookname, chapterLength))
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
        # print(data)
        webScrapToJSON(data[0], int(data[1]), currBookNo, version)
        print(f"Book number {currBookNo} loaded")
        currBookNo += 1

    print("Done Scrapping!")


def JsonToXML(version):
    print("Starting Loading...")
    folderlocation = f"{version}_tmpfolder"
    json_data = {}
    for book_number in range(1, 67):  # 66 books in the Bible
        try:
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
    # Enter what version for the website https://www.biblegateway.com You want to turn into an XML
    version = "AMPC"
    webScrap(version)
    JsonToXML(version)
    # postProcess(version) ### doesnt work
