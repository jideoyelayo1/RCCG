from bs4 import BeautifulSoup
import requests
import json
import os
import csv


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

    with open(f'AMPC_files/book{bookId}.json', 'w', encoding='utf-8') as json_file:
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


if __name__ == "__main__":
    print("Starting...")

    datas = Load_cvs()
    currBookNo = 1
    for data in datas:
        # print(data)
        webScrapToJSON(data[0], int(data[1]), currBookNo)
        print(f"Book number {currBookNo} loaded")
        currBookNo += 1

    print("Done!")
