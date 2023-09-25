xs = ["2peter","1james","3john","4jude","1john","2john","matthew","acts","psalms"]

def formatBookName(s):
    if not s[0].isdigit():
        return s[0].upper() + s[1:]
    else:
        return s[0] + " " + s[1].upper() + s[2:]

for x in xs:
    print(formatBookName(x))
