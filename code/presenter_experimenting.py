import pandas as pd
import numpy as np
import os
import re
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, groups_around_regex, clean_based_on_award_recipient, get_combinations, clean_based_on_award_subject, match_subsets, clean_based_on_award_recipient2, clean_based_on_award_subject2, split_on, handle_hashtags, handle_handles, made_for_tv, presenter_cleaner


def presenter_experimenting(tweets, award, regex_pairs):
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
    presenter_tweets = []
    prev_sub_len = len(award_pos_cleaned)
    while True:
        if counter == len(award_pos_cleaned):
            return(None)
        counter += 1

        sub_len = min(max(prev_sub_len - counter, 2), 4)
        prev_sub_len = sub_len

        terms_to_use = [list(x) for x in get_combinations(
            award_pos_cleaned, sub_len)]
        cleaned_terms_to_search = clean_based_on_award_subject2(
            clean_based_on_award_recipient2(terms_to_use, award), award)

        for subset in terms_to_use:
            presenter_tweets = np.concatenate(
                (presenter_tweets, filter_tweets(tweets, subset)), axis=0)

        if len(presenter_tweets) < 20:
            continue

        pd.DataFrame(data={'tweets': presenter_tweets}
                     ).to_csv(f'{award}_tweets.csv')

        # clean up the tweets
        cleaned_presenter_tweets = made_for_tv(clean_based_on_award_subject(
            clean_based_on_award_recipient(presenter_tweets, award), award), award)

        pd.DataFrame(data={'tweets': cleaned_presenter_tweets}
                     ).to_csv(f'{award}_presenters.csv')

        if len(cleaned_presenter_tweets) < 5:
            continue

        # use the given regex and group index to isolate a string that contains the winner's name
        potential_presenter_phrases = []
        for pair in regex_pairs:
            potential_presenter_phrases = potential_presenter_phrases + \
                groups_around_regex(cleaned_presenter_tweets, pair[0], pair[1])

        # print(potential_presenter_phrases)

        # Handle hashtags by spliting on new capitalization and include in potential winners

        potential_presenters = handle_hashtags(potential_presenter_phrases)
        potential_presenters = potential_presenters + \
            handle_handles(potential_presenter_phrases)

        # print(potential_presenters)

        # get the consecutive proper nouns from each of the strings potentially containing the winner's name
        potential_presenters = potential_presenters + get_consecutive_pos(
            potential_presenter_phrases, 'NNP')

        # print(potential_presenters)

        # print(potential_presenters)
        # cleaning proper nouns candidates list with terms that can't be winners
        cleaned = clean(
            potential_presenters, ['RT', '@', 'Golden', 'Globe', 'Award', 'HBO'])
        cleaned2 = exclude_award_name(cleaned, award)
        cleaned3 = presenter_cleaner(cleaned2)

        # get the frequency of counts for each nnp in the above list
        values, counts = np.unique(cleaned3, return_counts=True)

        # fuzzy match similar terms, giving precedence to the term with a higher count
        match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
        counts_dict, percent_dict = match_subsets(match_fuzzies)
        return(percent_dict)
