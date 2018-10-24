# topic-extraction


magic() from OCMagicTopics.py implements topic extraction by using the social tags from the free service Open Calais.
It accepts a string and outputs a dataframe of tags, and uses quick_clean.py. An additional file is needed and not included here: OpenCalaisLincenseKey.txt, which contains the titular information.

sp() from SpacyMethod.py approaches the problem by using spaCy, and operates under the assumption that the most-mentioned entities serve as good topics. In practice, this works quite well. Output is a dataframe with columns ['tag', 'type', 'score']. 'type' attempts to classify the tags (e.g. a tag of 'United States' has the type 'Location'), and 'score' is the normalized (continuous range of [0, 1]) number of appearances in the text.

oc() from OCMethod.py is also based around entities, but uses Open Calais to extract them. It also has an expanded range of possible 'type' values, and the ouputted dataframe has an additional column: 'remark'. If 'type' is 'City', 'remark' will (if Open Calais has the information) be the Country that that city is in. If 'type' is 'Person', 'remark' will (if Open Calais has the information) be the person's type ('Political','Economic', etc.).

All methods only return the top 10 topics.
