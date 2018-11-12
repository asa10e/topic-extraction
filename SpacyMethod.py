'''
May be necessary run the following bash commands:
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
'''
import re
import pandas as pd
from quick_clean import quick_clean
import spacy
import en_core_web_lg # large model performs better than small model
nlp = en_core_web_lg.load()
# import en_core_web_sm
# nlp = en_core_web_sm.load()
import logging
logger = logging.getLogger()
import country_converter as country_converter

def coco(name):
    """
    'U.S.','United States of America' -> 'United States', etc.
    """
    # Remove a leading "the" from names. Note that even for non-countries this is desirable for readability.
    name = re.sub(r'^(the\s)', '', name, flags=re.IGNORECASE)
    # Remove ending "'s" from names, which is present for some
    name = re.sub(r'''('s)$''', '', name)

    # Custom replacements that country_converter can't seem to handle
    custom_dic = {'US': 'United States','UK':'United Kingdom','EU':'European Union',
                    'E.U.':'European Union'}
    if name in custom_dic:
        name = custom_dic[name]

    logger.disabled = True # Fixes annoying warnings given by the country_converter module
    country = country_converter.CountryConverter().convert(name, to='name_short', not_found=None)
    logger.disabled = False

    return country

# A list of topics that, if identified, should not be shown to the user.
# TODO: Expand after extensive testing
stupid_topics = ['New York Times','Fox Business Network','CNN',
                'North','South','East','West']
# If these terms appear in the text, we will definitely include them as important topics
very_important_events = ['FOMC','Federal Open Market Committee',
                         'Jackson Hole',
                         'Trade War','Trade Tension','Protectionism',
                         'Brexit',
                         'Monetary Policy']
# Read in standardizations and store as a dictionary
reps = pd.read_csv('topic_name_mappings.csv')
replacements = dict(zip(reps.Name, reps.Standard))


def sp_text(text):
    """
    Outputs a dataframe of length <= 10 of tag, type, and score.
    The tag is a specific Person, Location, Event, or Other mentioned in the text.
    The type is literally either Person, Location, Event, or Other.
    The score is its normalized number of appearances (including mentions).
    """

    text = quick_clean(text) # Clean the text up
    doc = nlp(text)

    df = pd.DataFrame(columns = ['tag','type','score']) # Initialize df

    # We'll only accept these types of entities identified by spaCy
    readable_types = {'LOC':'Location','PERSON':'Person',
                    'ORG':'Institution','GPE':'Location',
                    'EVENT':'Event','WORK_OF_ART':'Other',
                    'LAW':'Other','PRODUCT':'Other',
                    'FAC':'Other'}
    good_labels = readable_types.keys() # 'LOC','PERSON', etc.

    # Create each column that will comprise the final dataframe
    # Use isspace() to get rid of repeated spaces like '  ' as an entity
    df['tag'] = [w.text for w in doc.ents if w.label_ in good_labels if not w.text.isspace()]
    df['type'] = [readable_types[w.label_] for w in doc.ents if w.label_ in good_labels if not w.text.isspace()]
    df['score'] = [df['tag'].values.tolist().count(e) for e in df['tag'].values.tolist()]

    # Standardize country names
    # Non-country names will not be affected other than a little cleaning (e.g. removing '^the')
    df['tag'] = df.tag.apply(coco)

    df = df[~df.tag.isin(stupid_topics)] # Remove stupid topics

    # Push to the top of df very_important_events, if they are in the text
    top_score = max(df.score)
    for e in very_important_events:
        if e.lower() in text.lower():
            new_row = [e, 'Event', top_score]
            df.loc[-1] = new_row # Create new row with index -1 (ensures a new index)
            # Now we shift the index up one, so -1 becomes 0
            # This is done before removing duplicates so that these very important events are not removed
            # They are classified as 'Event' and we don't want that to change.
            df.index = df.index + 1
            df = df.sort_index() # Push the important event to the top since it is now 0

    # Some custom replacements
    for r in replacements.keys():
        df = df.replace(r, replacements[r])

    df = df.drop_duplicates('tag') # Remove duplicates
    df = df.sort_values(by=['score'], ascending = False) # Sort by score

    # If both 'Jamal Khashoggi' and 'Khashoggi' are tags, we only want the longer of the two.
    # Similarly, we care about 'Saudi Arabia–United States relations' more than 'Saudi Arabia'.
    tag_lis = df.tag.values.tolist()
    tag_string = ' '+' '.join(tag_lis)+' ' # Combined string of all tags
    new_tag_lis = [t for t in tag_lis if tag_string.count(' '+t+' ')>1] # Only the tags that appear more than once
    df = df[~df.tag.isin(new_tag_lis)] # Remove those shorter tags

    df['score'] = df.score.apply(lambda x: round(x/max(df.score), 2)) # Normalize score

    df = df.drop_duplicates('tag').reset_index(drop=True) # Drop duplicated rows, if any

    df = df.head(10) # Take only the top 10 rows
    return df

def sp(text, title=''):
    """
    Runs sp_text() on both the text and title, but title is added twice to weight its importance.
    """
    if len(title)>0:
        text += ('. '+title)*2

    out_df = sp_text(text)

    return out_df


if __name__ == '__main__':
    sp()
