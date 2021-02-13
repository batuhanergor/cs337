import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award_recipient, get_combinations, clean_based_on_award_subject, match_subsets, clean_based_on_award_recipient2, clean_based_on_award_subject2, split_on, handle_hashtags, handle_handles, made_for_tv, presenter_cleaner


def get_winner_helper(tweets, award, regex_pairs):
    # break down the award name into proper nouns and adjectives
    award_pos = get_consecutive_pos(
        [award], 'NN') + get_consecutive_pos([award], 'JJ') + get_consecutive_pos([award], 'VBN')
    for term in award.split(' '):
        if '-' in term and term != '-':
            award_pos.append(term)

    # split pos into individual words (exclude "made")
    temp = []
    for term in [x.split(' ') if x !=
                 'cecil b.' and ' ' in x else x for x in award_pos]:
        if isinstance(term, str):
            temp.append(term)
        elif isinstance(term, list):
            temp += term
        # add regex for television vs. tv and mini-series vs. miniseries
    award_pos_cleaned = ['(television|tv)' if x ==
                         'television' else 'mini(-series|series)' if x == 'mini-series' else x for x in temp]

    # filter tweets for those containing all of the above nouns and adjective
    counter = 0
    award_tweets = []
    prev_sub_len = len(award_pos_cleaned)
    while True:
        # cap the iterations at 5 for time contraints
        if counter == len(award_pos_cleaned) or counter == 5:
            break

        sub_len = min(max(prev_sub_len - counter, 2), 4)
        prev_sub_len = sub_len
        terms_to_use = [list(x) for x in get_combinations(
            award_pos_cleaned, sub_len)]
        cleaned_terms_to_search = clean_based_on_award_subject2(
            clean_based_on_award_recipient2(terms_to_use, award), award)

        counter += 1
        for subset in cleaned_terms_to_search:
            award_tweets = np.concatenate(
                (award_tweets, filter_tweets(tweets, subset)), axis=0)

        if len(award_tweets) < 25:
            if counter < 10:
                continue
            else:
                return(None, None, None, None, None, None)

        pd.DataFrame(data={'tweets': award_tweets}
                     ).to_csv(f'{award}_tweets.csv')

        # clean up the tweets
        cleaned_winner_tweets = made_for_tv(clean_based_on_award_subject(
            clean_based_on_award_recipient(award_tweets, award), award), award)

        pd.DataFrame(data={'tweets': cleaned_winner_tweets}
                     ).to_csv(f'{award}_tweets_cleaned.csv')

        # use the given regex and group index to isolate a string that contains the winner's name
        potential_winners_phrases = []
        for pair in regex_pairs:
            potential_winners_phrases = potential_winners_phrases + \
                groups_around_regex(cleaned_winner_tweets, pair[0], pair[1])

        if award.lower() in ['best screenplay - motion picture', 'best original song - motion picture']:
            potential_winners_split = split_on(
                potential_winners_phrases, 'for', 1)
        else:
            potential_winners_split = potential_winners_phrases

        # Handle hashtags by spliting on new capitalization and include in potential winners
        potential_winners = handle_hashtags(potential_winners_split)
        potential_winners = potential_winners + \
            handle_handles(potential_winners_split)

        # print(potential_winners)

        # get the consecutive proper nouns from each of the strings potentially containing the winner's name
        potential_winners = potential_winners + get_consecutive_pos(
            potential_winners_split, 'NNP')

        # print(potential_winners)
        # cleaning proper nouns candidates list with terms that can't be winners
        cleaned = clean(
            potential_winners, ['RT', '@', 'Golden', 'Globe', 'Award', 'HBO', "'s"])
        cleaned2 = exclude_award_name(cleaned, award)

        # get the frequency of counts for each nnp in the above list
        values, counts = np.unique(cleaned2, return_counts=True)

        # fuzzy match similar terms, giving precedence to the term with a higher count
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
        counts_dict, percent_dict = match_subsets(match_fuzzies)

        # if only one candidate to return or if at least 25% split between top 2 candidates then return current dictionary
        if len(percent_dict.values()) < 2 or list(percent_dict.values())[0] / list(percent_dict.values())[1] >= 1.5:
            return(counts_dict)
        # otherwise, split on for to try to further isolate the real winner
        else:
            # print(counts_dict)
            # Handle hashtags by spliting on new capitalization and include in potential winners
            potential_winners_split = split_on(
                potential_winners_phrases, 'for', 0)
            potential_winners = handle_hashtags(potential_winners_split)

            # get the consecutive proper nouns from each of the strings potentially containing the winner's name
            potential_winners = potential_winners + get_consecutive_pos(
                potential_winners_split, 'NNP')

            # cleaning proper nouns candidates list
            cleaned = clean(
                potential_winners, ['RT', '@', 'Golden', 'Globe', 'Award', "'s"])
            cleaned2 = exclude_award_name(cleaned, award)

            # get the frequency of counts for each nnp in the above list
            values, counts = np.unique(cleaned2, return_counts=True)

            # fuzzy match similar terms, giving precedence to the term with a higher count
            match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
            counts_dict, percent_dict = match_subsets(match_fuzzies)

            # return a dictionary of candidates and counts
            # print(counts_dict)
            return(counts_dict)
