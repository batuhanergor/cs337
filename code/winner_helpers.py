import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award_recipient, get_combinations, clean_based_on_award_subject, match_subsets, split_on


def get_winner_by_keyword_regex(tweets, award, regex_pairs):
    # break down the award name into proper nouns and adjectives
    award_pos = get_consecutive_pos(
        [award], 'NN') + get_consecutive_pos([award], 'JJ')
    for term in award.split(' '):
        if '-' in term and term != '-':
            award_pos.append(term)

    # filter tweets for those containing all of the above nouns and adjective
    counter = 0
    # need to use terms_to_use to include other subsets if need be
    # putting outside loop so we can double count (in essence weight) tweets that have more of the terms
    award_tweets = []
    while True:
        if counter == len(award_pos):
            break
        terms_to_use = [list(x) for x in get_combinations(
            award_pos, min(len(award_pos) - counter, 10))]
        counter += 1
        for subset in terms_to_use:
            award_tweets = np.concatenate(
                (award_tweets, filter_tweets(tweets, subset)), axis=0)
        if len(award_tweets) < 15:
            print(counter)
            if counter < 5:
                continue
            else:
                return(None, None, None, None, None)

        # Use regex to filter the above tweets about the award to those that only mention a winner but exlude terms that don't imply a winner (negations, hope, should, etc.)
        winner_tweets = filter_tweets(filter_tweets(
            award_tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True), ["(should(\'ve| have)\s),(did(n\'t| not)\s),(hop(e|ing))"], exclude=True, _or=True)

        # clean up the tweets
        cleaned_winner_tweets = clean_based_on_award_subject(
            clean_based_on_award_recipient(winner_tweets, award), award)

        pd.DataFrame(data={'tweets': winner_tweets}
                     ).to_csv(f'{award}_tweets.csv')

        if len(cleaned_winner_tweets) < 10:
            # print(counter)
            if counter < 5:
                continue
            # eventually give up if nothing signicant can be found in order to run the rest of the program
            else:
                return(None, None, None, None, None)

        # use the given regex and group index to isolate a string that contains the winner's name
        potential_winners = []
        for pair in regex_pairs:
            potential_winners = potential_winners + \
                groups_around_regex(cleaned_winner_tweets, pair[0], pair[1])

        # get the consecutive proper nouns from each of the strings potentially containing the winner's name
        nnp_potential_winners = get_consecutive_pos(
            potential_winners, 'NNP')
        # cleaning proper nouns candidates list
        cleaned = clean(
            nnp_potential_winners, ['RT', '@', 'Golden', 'Globe', 'Award'])
        cleaned2 = exclude_award_name(cleaned, award)

        # get the frequency of counts for each nnp in the above list
        values, counts = np.unique(cleaned2, return_counts=True)

        # fuzzy match similar terms, giving precedence to the term with a higher count
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
        combine_subsets = match_subsets(match_fuzzies)

        # return a dictionary of candidates and counts
        return(combine_subsets, nnp_potential_winners, potential_winners, winner_tweets, award_pos)


def get_winner_by_consecutive_pos(tweets, award):

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
        counter += 1
        award_tweets = []
        for subset in terms_to_use:
            award_tweets = np.concatenate(
                (award_tweets, filter_tweets(tweets, subset)), axis=0)
        if len(award_tweets) < 25:
            continue

        # Use regex to filter the above tweets about the award to those that only mention a winner but exlude terms that don't imply a winner (negations, hope, should, etc.)
        winner_tweets = clean_based_on_award_subject(clean_based_on_award_recipient(filter_tweets(filter_tweets(
            award_tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True), ["(should(\'ve| have)\s),(did(n\'t| not)\s),(hop(e|ing))"], exclude=True, _or=True), award), award)

        candidates = get_consecutive_pos(winner_tweets, 'NNP')
        cleaned = clean(
            candidates, ['RT', '@', 'Golden', 'Globe', 'Award', '#'])
        cleaned2 = clean(cleaned, award_pos)
        cleaned3 = exclude_award_name(cleaned, award)
        values, counts = np.unique(cleaned3, return_counts=True)
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
        return(match_fuzzies)


def combine_preds(preds):
    to_return = {}
    for pred_dict in preds:
        for key in pred_dict.keys():
            if key in to_return:
                to_return[key] += pred_dict[key]
            else:
                to_return[key] = pred_dict[key]
    return({k: v for k, v in sorted(to_return.items(), key=lambda x: x[1], reverse=True)})
