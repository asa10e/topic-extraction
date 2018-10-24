import requests
import re
import pandas as pd
from quick_clean import quick_clean
# license_key = open('OpenCalaisAPIKey.txt', 'r').read()
license_key = 'HNAKYRPhvpGID9NcMSelWTEO2W6r0Tfh'
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

def entity_dataframe_maker(doc):

    df = pd.DataFrame(columns = ['tag','type','remark','score'])

    for subdic in doc:

        try:
            if (doc[subdic]['forenduserdisplay'] == 'true') & (doc[subdic]['_typeGroup'] == 'entities'):
                row = [doc[subdic]['name'], doc[subdic]['_type']]

                # Resolutions to populate remark column of our dataframe
                # Cities and states:
                if doc[subdic]['_type'] in ['City','ProvinceOrState']:
                    try:
                        # Make the remark equal to the country the city is in
                        row.append(doc[subdic]['resolutions'][0]['containedbycountry'])
                    except:
                        row.append(None)

                elif doc[subdic]['_type'] in ['Person']:
                    try:
                        # If possible, make the remark equal to the type of person, e.g. political
                        if doc[subdic]['persontype'] != 'N/A':
                            row.append(doc[subdic]['persontype'])
                    except:
                        row.append(None)

                else:
                    row.append(None)

                # score
                try:
                    row.append(doc[subdic]['relevance'])
                except:
                    row.append(None)

                df.loc[len(df)] = row
        except:
            pass

    return df


def oc(text):

    text = quick_clean(text)
    doc = get_json(text)
    df = entity_dataframe_maker(doc)

    df = df.sort_values(by=['score'], ascending = False).reset_index(drop=True)

    df['score'] = df.score.apply(lambda x: round(x/max(df.score),2)) # Normalize score
    df = df[['tag','type','score','remark']]
    df = df.head(10)
    return df


if __name__ == '__main__':
    oc()
