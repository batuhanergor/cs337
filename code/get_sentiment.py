from filter_tweets import filter_tweets, capture_groups, lowercase_array
import numpy as np
import re
import nltk
import pandas as pd
from textblob import TextBlob

def load_tweets2(filename):
    return pd.read_json(filename)

def get_sentiment(year):
    return load_tweets2('../data/gg2013.json')

df = get_sentiment(0)
df.text = df.text.map(lambda x: re.sub("(?i)best", '', x))
groups = df.groupby(df.timestamp_ms.dt.floor('15min')).indices
for x in groups:
    print(len(groups[x]))
    print(df[df.index.isin(groups[x])].text.map(lambda x: TextBlob(x).sentiment.polarity).mean())
    # print(df[df.index.isin(groups[x])])
