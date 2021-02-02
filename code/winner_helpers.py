import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award, get_combinations


def get_winner_by_keyword_regex(tweets, award, regex_pairs):
    # break down the award name into proper nouns and adjectives
    award_pos = get_consecutive_pos(
        [award], 'NN') + get_consecutive_pos([award], 'JJ')

    # filter tweets for those containing all of the above nouns and adjective
    # will need a method to relax this filtering if not enough results are returned
    counter = 0
    # need to use terms_to_use to include other subsets if need be
    while True:
        if counter == len(award_pos):
            break
        terms_to_use = [list(x) for x in get_combinations(
            award_pos, len(award_pos) - counter)]
        print(terms_to_use)
        counter += 1
        award_tweets = []
        for subset in terms_to_use:
            award_tweets = np.concatenate(
                (award_tweets, filter_tweets(tweets, subset)), axis=0)
        print(len(award_tweets))
        if len(award_tweets) < 25:
            continue

        # Use regex to filter the above tweets about the award to those that only mention a winner but exlude terms that don't imply a winner (negations, hope, should, etc.)
        winner_tweets = clean_based_on_award(filter_tweets(filter_tweets(
            award_tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True), ["(should(\'ve| have)\s),(did(n\'t| not)\s),(hop(e|ing))"], exclude=True, _or=True), award)

        # use the given regex and group index to isolate a string that contains the winner's name
        potential_winners = []
        for pair in regex_pairs:
            potential_winners = potential_winners + \
                groups_around_regex(winner_tweets, pair[0], pair[1])

        # get the consecutive proper nouns from each of the strings potentially containing the winner's name
        nnp_potential_winners = get_consecutive_pos(potential_winners, 'NNP')

        # cleaning proper nouns candidates list
        cleaned = clean(
            nnp_potential_winners, ['RT', '@', 'Golden', 'Globe', 'Award', '#'])
        cleaned2 = exclude_award_name(cleaned, award)

        # get the frequency of counts for each nnp in the above list
        values, counts = np.unique(cleaned2, return_counts=True)

        # fuzzy match similar terms, giving precedence to the term with a higher count
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)

        # return a dictionary of candidates and counts
        return(match_fuzzies)
