import re

def extract_first_verse(text):
    match = re.search(r'\d+([A-Z].*?)(?=\d+[A-Z]|$)', text)
    if match:
        verse_text = match.group(1).strip()
        return verse_text
    else:
        return None

text = "25And Joseph took an oath from the sons of Israel, saying, God will surely visit you, and you will carry up my bones from here.26So Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt."
text2 = "26So Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt."
result = extract_first_verse(text)
result2 = extract_first_verse(text2)
print(result)
print(result2)
