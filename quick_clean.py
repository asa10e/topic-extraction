import re
from unidecode import unidecode
def quick_clean(text):

    text = unidecode(text) # Replaces stuff like smart quotes with stuff like simple quotes
    text = re.sub(r'\s+', ' ', text) # Get rid of extra whitespace and newlines

    text = text.replace('For best results when printing this announcement, please click on link below:', ' ')
    text = re.sub(r'^\((.*?)\)',' ', text) # Remove ^('text')

    text = text.lstrip() # Trim leading whitespace, which allows the following few lines to work
    text = re.sub(r'^By\s[a-zA-Z]+\s[a-zA-Z]+\s', '', text) # Removes ^By Asa Tenney
    text = re.sub(r'^[a-zA-Z]+\s+[a-zA-Z]+,\s[a-zA-Z]{3}\s\d{1,2}', ' ', text) # Removes ^VATICAN CITY, Jan 26
    text = re.sub(r'^[a-zA-Z]+\s+[a-zA-Z]+\s\(Reuters\)', ' ', text)
    text = re.sub(r'^[a-zA-Z]+,\s[a-zA-Z]{3,8}\s\d{1,2}', ' ', text) # Removes ^BEIJING, Jan 26
    text = re.sub(r'^[a-zA-Z]+\s\(Reuters\)', ' ', text)

    text = text.replace('\n', ' ')
    text = re.sub(r'\((.*?)\)',' ', text) # Remove ('text')
    text = re.sub(r'\[(.*?)\]',' ', text) # Remove ['text']
    text = re.sub(r'<(.*?)>',' ', text) # Remove <'text'>
    text = re.sub(r'\S*@\S*\s?', ' ', text) # Remove emails
    text = re.sub(r'http\S+', ' ', text) # Remove URLs
    text = re.sub(r'(reuters)', ' ', text, flags=re.IGNORECASE)
    text = text.replace('Breakingviews', ' ')

    text = re.sub(r'''[^a-zA-Z0-9.,;'":$]+''', ' ', text)
    return text
