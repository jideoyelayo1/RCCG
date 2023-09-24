import re

def extract_first_verse(text):
    match = re.search(r'\d+([A-Za-z].*?)(?=\d+[A-Za-z]|$)', text)
    if match:
        verse_text = match.group(1).strip()
        return verse_text
    else:
        return None

texts = ["25and Joseph took an oath from the sons of Israel, saying, God will surely visit you, and you will carry up my bones from here.26so Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt.", "26So Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt.", "26so Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt.","25And Joseph took an oath from the sons of Israel, saying, God will surely visit you, and you will carry up my bones from here.26So Joseph died, being 110 years old; and they embalmed him, and he was put in a coffin in Egypt."]
results = [extract_first_verse(x) for x in texts]
for result in results:
	print(1,result)

