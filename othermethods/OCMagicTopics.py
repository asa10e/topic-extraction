import requests
import re
import pandas as pd
from quick_clean import quick_clean
license_key = open('OpenCalaisLincenseKey.txt', 'r').read()
calais_url = 'https://api.thomsonreuters.com/permid/calais'

def get_json(content):
    '''
    Given a string, returns the raw json response from Open Calais
    '''
    headers = {'Content-Type': 'text/raw',
                    'omitOutputtingOriginalText': 'true',
                    'outputFormat': 'application/json',
                    'x-ag-access-token': license_key,
                    'x-calais-contentClass': 'news',
                    'x-calais-language':'English'
}
    r = requests.post(calais_url,
                    headers=headers,
                    data=content)

    doc = r.json()
    return doc

# We'll remove these if they come up. We can add to this list as we come across more topics we aren't interested in.
stupid_topics = ['Economy','Finance','Money','Banking','Banks','Marketing','Politics','Macroeconomics',
                    'Bank','Business','Economics', # 'Central bank',
                    'Financial economics','PR Newswire','Breakingviews','Modern history',
                    '21st century in the United States',#'Chinese people',
                    'Geography of Asia','Western Asia','Republics','Member states of the United Nations',
                    'Americas','Asia','Military history by country','Foreign exchange market',
                    'Benchmark','Currency','History by period','Universe','Nature','Chronology of world oil market events'
                    # 'Dollar','Pound sterling','Malaysian ringgit'
                    ]
def magic(text):

    text = quick_clean(text)

    doc = get_json(text)

    df = pd.DataFrame(columns = ['tag','score'])

    for subdic in doc:
        try:
            if (doc[subdic]['forenduserdisplay'] == 'true') & (doc[subdic]['_typeGroup'] == 'socialTag'):
                row = [doc[subdic]['name'], doc[subdic]['importance']]

                df.loc[len(df)] = row
        except:
            pass

    df = df[~df.tag.isin(stupid_topics)] # remove stupid topics

    # If both 'Jamal Khashoggi' and 'Khashoggi' are tags, we only want the longer of the two.
    # Similarly, we care about 'Saudi Arabia–United States relations' more than 'Saudi Arabia'.
    tag_lis = df.tag.values.tolist()
    tag_string = ' '.join(tag_lis)
    new_tag_lis = [t for t in tag_lis if tag_string.count(t)>1]
    df = df[~df.tag.isin(new_tag_lis)] # Remove those shorter tags

    df = df.sort_values(by=['score'], ascending = False).reset_index(drop=True)
    df = df.head(10) # Only take the top 10

    df = df.drop(['score'], axis = 1) # Drop the score column for now. Not really that useful

    return df


if __name__ == '__main__':
    magic()
