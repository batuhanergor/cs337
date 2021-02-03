import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award
from winner_helpers import get_winner_by_keyword_regex


def get_winners(award_names, tweets):
    for idx, award in enumerate(award_names):
        print(
            f'Award {idx + 1} of {len(award_names)}: {award.title()}')
        regex_winners = get_winner_by_keyword_regex(
            tweets, award, [('(wins|receives)', 0), ('(goes|went) to', -1)])
        # print(regex_winners)

        """
        cg = get_consecutive_pos(winner_tweets, 'NNP')
        cleaned = clean(cg, ['RT', '@', 'Golden', 'Globe', 'Award', '#'])
        cleaned2 = clean(cleaned, award_pos)
        cleaned3 = exclude_award_name(cleaned, award)
        values, counts = np.unique(cleaned3, return_counts=True)
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
        print(match_fuzzies)
        print(
            f'\t{award.title()} $$$ {list(match_fuzzies.keys())[0].title()}')
        """


# Notes for determining award
"""
Need different approaches for awards won by a person and awards won by a movie
General Approach:
    1) Filter for tweets that contain the name of the award
        # POS tagged
        # iterate through POS's and try leaving out more and more of a subset
    2) Remove tweets that have negatives, such a Didn't, Should have, etc.
    3) Remove specific phrases from tweets before trying regex matching
        * Name of award, Golden Globes
    4) Look most commonly occuring substring (how to determine substring)
        * Consecutive NNPs?
        * Use POS tagging and look for NNP "wins/receives" NNP
"""


if __name__ == "__main__":

    OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
    OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy',
                            'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets13 = load_tweets('data/gg2013.json')
# answers13 = load_answers('data/gg2013.json')
get_winners(OFFICIAL_AWARDS_1315, tweets13)
# get_winners(["best motion picture - comedy or musical"], tweets13)