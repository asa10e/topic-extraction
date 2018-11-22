import re
def quick_clean(text):

    text = re.sub(r'\s+', ' ', text) # Get rid of extra whitespace and newlines
    text = re.sub(r'^(.*\(Reuters\))','',text) # Just get rid of everything before the (Reuters)
    text = re.sub(r'^(.*\(Bloomberg\))','',text) # Just get rid of everything before the (Bloomberg)
    text = text.replace('For best results when printing this announcement, please click on link below:', ' ')

    # These subs get rid of the reporter and editor names at the end of Bloomberg articles
    text = re.sub(r'(To contact the reporters on this story:.*)','',text, flags=re.DOTALL)
    text = re.sub(r'(-With assistance from.*)','',text, flags=re.DOTALL)
    text = re.sub(r'(Read morehere.*)','',text, flags=re.DOTALL)

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
