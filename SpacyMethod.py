import re
import pandas as pd
from quick_clean import quick_clean
import spacy
import en_core_web_lg # large model performs better than small model
nlp = en_core_web_lg.load()
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

    # If multiple countries are identified, a list of them is returned
    # we'll just take the first country identified in this case
    if type(country) == list:
        country = country[0]

    return country

location_names = list(pd.read_csv('location_names.csv', header = None).iloc[:,0])

# A list of topics that, if identified, should not be shown to the user.
stupid_topics = ['New York Times','Fox Business Network','CNN','Wall Street Journal','Sky News',
                'Business Day','Twitter','S P','SIGN','BREAKINGVIEWS','Group']
# If these terms appear in the text, we will definitely include them as important topics
very_important_events = ['FOMC','Federal Open Market Committee',
                         'Jackson Hole',
                         'Trade War','Trade Tension','Protectionism',
                         'Brexit',
                         'Monetary Policy',
                         'Belt and Road']
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

    # First remove any tag that is equal to one of four trouble words
    # Then remove any tag that contains an element in stupid_topics
    df = df[~df.tag.isin(['North','South','East','West'])]
    df = df[~df.tag.map(lambda x: any([top in x for top in stupid_topics]))]

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
        df['tag'] = df.tag.apply(lambda x: replacements[r] if r in x else x)
        # df = df.replace(r, replacements[r])

    df = df.drop_duplicates('tag').reset_index(drop=True) # Drop duplicated tags, if any

    # If both 'Jamal Khashoggi' and 'Khashoggi' are tags, we only want the longer of the two.
    # Similarly, we care about 'Saudi Arabia–United States relations' more than 'Saudi Arabia'.
    tag_lis = df.tag.values.tolist()
    tag_string = ' '+'  '.join(tag_lis)+'  ' # Combined string of all tags
    new_tag_lis = [t for t in tag_lis if tag_string.count(' '+t+' ')>1] # Only the tags that appear more than once
    df = df[~df.tag.isin(new_tag_lis)] # Remove those shorter tags

    df = df.sort_values(by=['score'], ascending = False) # Sort by score
    df = df.drop_duplicates('tag').reset_index(drop=True) # Drop duplicated tags, if any

    # Known country names should have type 'Location' regardless of what spaCy says
    locs_in_df = [t for t in df.tag if t in location_names]
    for c in locs_in_df:
        idx = df.loc[df['tag']== c].index[0] # We know there's only one since we dropped duplicates
        df.at[idx,'type'] = 'Location' # Set type to Location

    # Drop any tag that contains a number
    bad_tags = []
    for t in df.tag.values.tolist():
        if bool(re.match(r'.*\d.*',t)): # If a number is in the tag
            bad_tags.append(t) # Add to bad_tags
    df = df[~df['tag'].isin(bad_tags)] # Drop anything in bad_tags

    # If a tag is in all caps and has a non-all caps duplicate, drop the all caps tag
    bad_tags = []
    all_tags = df.tag.values.tolist()
    all_tags_lowered = [t.lower() for t in all_tags]
    for t in all_tags:
        if (t.upper() in all_tags) & (all_tags_lowered.count(t.lower()) > 1):
            bad_tags.append(t.upper())
    df = df[~df['tag'].isin(bad_tags)] # Drop anything in bad_tags

    # Remove punctuation from tags, and strip leading and trailing whitespace
    df['tag'] = df['tag'].apply(lambda x: (re.sub(r'[^a-zA-Z ]', '', x)).strip())

    df = df.reset_index(drop=True) # Reset index a final time
    # Display capitalized tags nicer
    cap_cleaner = lambda t: t.title() if ((t == t.upper()) & (len(t.split())>1)) else t
    for i in range(len(df)):
        df.loc[i,'tag'] = cap_cleaner(df.loc[i,'tag'])

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
