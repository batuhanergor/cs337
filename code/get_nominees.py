from filter_tweets import filter_tweets, capture_groups, lowercase_array
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import pandas as pd
import os
import re
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, clean_based_on_award, get_combinations
import nltk
from collections import Counter


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets = load_tweets(f'../data/gg{2013}.json')

for idx, award in enumerate(OFFICIAL_AWARDS_1315):
    #print(f'Award {idx + 1} of {len(OFFICIAL_AWARDS_1315)}: {award.title()}')
    # break down the award name into proper nouns and adjectives
    award_pos = get_consecutive_pos(
        [award], 'NN') + get_consecutive_pos([award], 'JJ')
    # filter all tweets to find all tweets including "nominations", and exclude negations, and clean from award names
    nominee_tweets = clean_based_on_award(filter_tweets(filter_tweets(
        tweets, ["nomin(ee|ees|ated|ation)", "should have won"], _or=True), award_pos, exclude=False, _or=True), award)
    # exclude all tweets with "should have won"
    nominee_tweets2 = clean_based_on_award(filter_tweets(tweets,["should have won"], exclude = False, _or = True), award)
    nominee_tweets3 = nominee_tweets.append(nominee_tweets2)
    cleaned2 = clean_based_on_award(nominee_tweets3, award)

    # capture group with all with pattern in numpy array and convert to list
    captured_groups = capture_groups(cleaned2,  "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+))")
    captured_groups_list = captured_groups.tolist()

    # convert list to lower case
    captured_groups_list1 = [item.lower() for item in captured_groups_list]
    data = exclude_award_name(captured_groups_list1, award_pos)
    data1 = exclude_award_name(captured_groups_list1, ["RT", "golden globes", "golden awards", "globes awards", "golden globe", "award", "awards"])
    print("AWARED POS: ", award_pos)
    # find word counts of each element in list
    word_freq = Counter(data1)

#    print("AWARD: ", idx, award)
#    print("COUNTER: ", word_freq)
    for i in range(4):
        print("hay", word_freq.most_common()[i])