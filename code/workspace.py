import pandas as pd
import numpy as np
import os
import re
import Levenshtein
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import regex_filter, remove_part_of_tweet, levenshtein_dict, get_consecutive_pos, clean, exclude_award_name, leave_one_out, check_answer, groups_around_regex, clean_based_on_award_subject, clean_based_on_award_recipient
from winner_helpers import get_winner_by_keyword_regex, get_winner_by_consecutive_pos, combine_preds
from experiment import experimenting
from presenter_experimenting import presenter_experimenting


def get_winners(award_names, tweets, winners):

    # Use regex to filter the above tweets about the award to those that only mention a winner but exlude terms that don't imply a winner (negations, hope, should, etc.)
    possible_winning_tweets = filter_tweets(
        tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True)

    winner_tweets = filter_tweets(possible_winning_tweets, [
                                  "(should(\'ve| have)\s),(did(n\'t| not)\s),(hop(e|ing))"], exclude=True, _or=True)

    to_return = {}

    for idx, award in enumerate(award_names):
        print(f'Award {idx + 1} of {len(award_names)}: {award.title()}')
        # try specific approach for Best Screenplay - Motion Picture and best original song - motion picture
        if award.lower() in ['best screenplay - motion picture', 'best original song - motion picture']:
            winner_preds, percents_dict, potential_winners, potential_winners, returned_winner_tweets, award_pos = experimenting(
                winner_tweets, award, [('(.*)(goes|went) to (.*)for(.*?)', -1), ('(.*)(wins|won|receives)(.*)for(.*?)', -1), ('(.*)by(.*)', 0), ('(wins|won|receives)', 0), ('(goes|went) to', -1), ('winne(r|rs) (is|are)', -1)])
        else:
            winner_preds, percents_dict, potential_winners, potential_winners, returned_winner_tweets, award_pos = experimenting(
                winner_tweets, award, [('(wins|won|receives)', 0), ('(goes|went) to', -1), ('winne(r|rs) (is|are)', -1), ('winner, (.*) is', -1)])

        try:
            winner = list(combine_preds([winner_preds]).keys())[0]
        except Exception as e:
            winner = None

        to_return[award] = winner

        """
        if winner.lower() == winners[award]:
            print(winner)
        else:
            print(f'\t{winner.lower().title()}', winner_preds,
                  winner_preds[winner]/sum([v for k, v in winner_preds.items()]), sum([v for k, v in winner_preds.items()]), winners[award])
        """
    return(to_return)

    # Notes for determining award


def get_presenters(award_names, tweets, presenters):

    # Use regex to filter the above tweets about the award to those that only mention a winner but exlude terms that don't imply a winner (negations, hope, should, etc.)
    possible_presenter_tweets = filter_tweets(
        tweets, ["presen(ts|ter|ters|ted|ting|ta)"], _or=True)

    pd.DataFrame(data={'text': possible_presenter_tweets}
                 ).to_csv('possible_presenter_tweets.csv')

    to_return = {}
    for idx, award in enumerate(award_names):
        print(f'Award {idx + 1} of {len(award_names)}: {award.title()}')
        percents_dict = presenter_experimenting(
            possible_presenter_tweets, award, [('present(s|ed)', 0), ('presenting (.*) (is|are)', -1), ('presenting', 0)])
        to_return[award] = (percents_dict)
    return(to_return)


def finalize_presenters(winners, presenters):
    to_return = {}
    for award in winners.keys():
        potentials = {}
        winner = winners[award]
        potential_presenters = presenters[award]
        if potential_presenters:
            for pp in potential_presenters.keys():
                if Levenshtein.ratio(winner.lower(), pp.lower()) < 0.75:
                    potentials[pp] = potential_presenters[pp]
            presenters_to_return = []
            percent = 1.0
            for key, value in potentials.items():
                if len(presenters_to_return) == 0:
                    presenters_to_return.append(key)
                    if value > 0.65:
                        break
                    percent = value
                else:
                    if percent - value < 0.3:
                        presenters_to_return.append(key)
                if len(presenters_to_return) == 2:
                    break
            to_return[award] = presenters_to_return
        else:
            to_return[award] = []
    return(to_return)


if __name__ == "__main__":

    OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
    OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy',
                            'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets13 = load_tweets('data/gg2013.json')
# pd.DataFrame(data={'text': tweets13}).to_csv('tweets13.csv')
answers13 = load_answers('data/gg2013answers.json')
winners = answers13['winner']
presenters = answers13['presenters']
predicted_winners = get_winners(OFFICIAL_AWARDS_1315, tweets13, winners)
predicted_presenters = get_presenters(
    OFFICIAL_AWARDS_1315, tweets13, presenters)
print(predicted_presenters)
predicted_presenters2 = finalize_presenters(
    predicted_winners, predicted_presenters)
print(predicted_presenters2)

"""
tweets15 = load_tweets('data/gg2015.json')
answers15 = load_answers('data/gg2015answers.json')
winners = answers15['winner']
presenters = answers15['presenters']
predicted_winners = get_winners(OFFICIAL_AWARDS_1315, tweets15, winners)
predicted_presenters = get_presenters(
    OFFICIAL_AWARDS_1315, tweets15, presenters)
predicted_presenters2 = finalize_presenters(
    predicted_winners, predicted_presenters)
print(predicted_presenters2)
"""
