import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award_subject, clean_based_on_award_recipient
from winner_helpers import get_winner_by_keyword_regex, get_winner_by_consecutive_pos, combine_preds


def get_winners(award_names, tweets, winners):

    for idx, award in enumerate(award_names):
        print(
            f'Award {idx + 1} of {len(award_names)}: {award.title()}')
        winner_preds, nnp_potential_winners, potential_winners, winner_tweets, award_pos = get_winner_by_keyword_regex(
            tweets, award, [('(wins|receives)', 0), ('(goes|went) to', -1)])
        # method2 = get_winner_by_consecutive_pos(tweets, award)
        winner = list(combine_preds([winner_preds]).keys())[0]
        try:
            winner = list(combine_preds([winner_preds]).keys())[0]
        except IndexError as e:
            print(e)
            winner = None

        if winner.lower() != winners[award]:
            print(award_pos, potential_winners,
                  nnp_potential_winners, winner_preds, winners[award])


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
    4) Look most commonly occuring substring(how to determine substring)
        * Consecutive NNPs?
        * Use POS tagging and look for NNP "wins/receives" NNP


"""


if __name__ == "__main__":

    OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
    OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy',
                            'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets13 = load_tweets('data/gg2013.json')
answers13 = load_answers('data/gg2013answers.json')
winners = answers13['winner']
get_winners(OFFICIAL_AWARDS_1315, tweets13, winners)
# get_winners(["best motion picture - comedy or musical"], tweets13)
