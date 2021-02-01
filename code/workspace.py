import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name


def keyword_filter(df, keywords=[], method='or'):
    df = pd.DataFrame(data={'text': df})
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


"""
def regex_filter(df, start, end):
    to_return = pd.DataFrame([])
    for _, row in df.iterrows():
        x = re.search(fr'{start}\.(.*?){end}', row['text'])
        if x:
            print(row)
            print(x)
            break
"""


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


if __name__ == "__main__":

    OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets13 = load_tweets('data/gg2013.json')

# try getting winners
for idx, award in enumerate(OFFICIAL_AWARDS_1315):
    print(f'Award {idx + 1} of {len(OFFICIAL_AWARDS_1315)}')
    award_nns = get_consecutive_pos([award], 'NN')
    award_jjs = get_consecutive_pos([award], 'JJ')
    award_pos = award_nns + award_jjs
    print(award_pos)
    award_tweets = filter_tweets(tweets13, award_pos)
    winner_tweets = filter_tweets(
        award_tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True)
    winner_tweets = filter_tweets(
        winner_tweets, ["(should(\'ve| have)\s),(did(n\'t| not)\s)"], exclude=True, _or=True)
    """
    cg = capture_groups(
        winner_tweets, "([A-Z][a-z]+(\s[A-Z][a-z]*)*)")
    """
    cg = get_consecutive_pos(winner_tweets, 'NNP')
    cleaned = clean(cg, ['RT', '@', 'Golden', 'Globe', 'Award', '#'])
    cleaned2 = exclude_award_name(cleaned, award)
    values, counts = np.unique(cleaned2, return_counts=True)
    match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
    print(
        f'\t{award.title()} $$$ {list(match_fuzzies.keys())[0].title()}')


# Notes for determining award
"""
Need different approaches for awards won by a person and awards won by a movie

General Approach:
    1) Filter for tweets that contain the name of the award
    2) Remove tweets that have negatives, such a Didn't, Should have, etc.
    3) Remove specific phrases from tweets before trying regex matching
        * Name of award, Golden Globes
    4) Look most commonly occuring substring (how to determine substring)
        * Consecutive NNPs?
        * Use POS tagging and look for NNP "wins/receives" NNP


"""
