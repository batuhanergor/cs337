import pandas as pd
import numpy as np
import os
import re
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from load_tweets_and_answers import load_tweets, load_answers


def keyword_filter(df, keywords=[], method='or'):
    to_return = pd.DataFrame([])
    if method == 'or':
        for keyword in keywords:
            to_return = to_return.append(df[df['text'].str.lower(
            ).str.contains(keyword)])
    if method == 'and':
        to_return = df.copy(deep=True)
        for keyword in keywords:
            to_return = to_return[to_return['text'].str.lower(
            ).str.contains(keyword)]
    return(to_return)


def regex_filter(df, start, end):
    to_return = pd.DataFrame([])
    for _, row in df.iterrows():
        x = re.search(fr'{start}\.(.*?){end}', row['text'])
        if x:
            print(row)
            print(x)
            break


def get_pos(df, pos):
    to_return = []
    for _, row in df.iterrows():
        tags = nltk.pos_tag(nltk.word_tokenize(
            re.sub('[^A-Za-z ]+', '', row['text'])))
        proper_nouns = [x[0] for x in tags if x[1] == pos and x[0].lower() not in (
            ['golden', 'globes', 'goldenglobes', 'rt'])]
        to_return.extend(proper_nouns)
    return(to_return)


def get_top_k(input_list, k):
    elements, counts = np.unique(input_list, return_counts=True)
    zipped = list(zip(elements, counts))
    ordered = sorted(zipped, key=lambda x: x[1], reverse=True)
    return(ordered[:k])


def try_get_hosts():
    host_filter = keyword_filter(gg2013, ['host', 'golden globes'], 'and')
    pns = get_pos(host_filter, 'NNP')
    top_pns = get_top_k(pns, 10)
    print(top_pns)

    #hist_filter2 = keyword_filter(gg2013, ['host the '])


if __name__ == "__main__":
    gg2013 = pd.DataFrame(load_tweets('data/gg2013.json'))
    gg2015 = pd.DataFrame(load_tweets('data/gg2015.json'))

    # Try Getting Hosts
    try_get_hosts()

    # trouble with getting only first names and only last names

    # Try Getting Awards
    #regex_filter(gg2013, 'nominees for', 'are')
