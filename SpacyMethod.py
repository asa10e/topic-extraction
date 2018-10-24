'''
May be necessary run the following bash commands:
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
'''
import re
import pandas as pd
from quick_clean import quick_clean
import spacy
import en_core_web_lg # large model performs better
nlp = en_core_web_lg.load()
# import en_core_web_sm
# nlp = en_core_web_sm.load()
import logging
logger = logging.getLogger()
import country_converter as country_converter

def coco(name):
    '''
    'U.S.' -> 'United States', etc.
    '''

    name = re.sub(r'^(the\s)', '', name, flags=re.IGNORECASE)

    # Custom replacements
    custom_dic = {'US': 'United States','UK':'United Kingdom','EU':'European Union',
                    'E.U.':'European Union'}
    if name in custom_dic:
        name = custom_dic[name]

    logger.disabled = True # Fixes annoying warnings given by the country_converter module
    country = country_converter.CountryConverter().convert(name, to='name_short', not_found=None)
    logger.disabled = False

    return country

stupid_topics = ['New York Times','Fox Business Network','CNN',
                'North','South','East','West']

def sp(text):

    text = quick_clean(text)
    doc = nlp(text)

    df = pd.DataFrame(columns = ['tag','type','score']) # Initialize df

    # We'll only accept these types of entities identified by spaCy
    readable_types = {'LOC':'Location','PERSON':'Person',
                    'ORG':'Institution','GPE':'Location',
                    'EVENT':'Event','WORK_OF_ART':'Other',
                    'LAW':'Other','PRODUCT':'Other',
                    'FAC':'Other'}
    good_labels = readable_types.keys()

    df['tag'] = [w.text for w in doc.ents if w.label_ in good_labels if not w.text.isspace()] # use isspace to get rid of crap like '  ' as an entity

    df['type'] = [readable_types[w.label_] for w in doc.ents if w.label_ in good_labels if not w.text.isspace()]

    df['score'] = [df['tag'].values.tolist().count(e) for e in df['tag'].values.tolist()]

    # Clean up
    df = df.drop_duplicates('tag') # Remove duplicates
    df = df.sort_values(by=['score'], ascending = False) # Sort by score


    df['tag'] = df.tag.apply(coco) # Standardize country names

    df = df[~df.tag.isin(stupid_topics)] # remove stupid topics

    # if both 'Jamal Khashoggi' and 'Khashoggi' are tags, we only want the longer of the two.
    # Similarly, we care about 'Saudi Arabia–United States relations' more than 'Saudi Arabia'.
    tag_lis = df.tag.values.tolist()
    tag_string = ' '.join(tag_lis)
    new_tag_lis = [t for t in tag_lis if tag_string.count(t)>1]
    df = df[~df.tag.isin(new_tag_lis)] # Remove those shorter tags

    df['score'] = df.score.apply(lambda x: round(x/max(df.score), 2)) # Normalize score


    df = df.drop_duplicates('tag').reset_index(drop=True)

    df = df.head(10)
    return df


if __name__ == '__main__':
    sp()
