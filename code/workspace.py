import pandas as pd
import numpy as np
import os
import re
import Levenshtein
from load_tweets_and_answers import load_tweets, load_answers
from filter_tweets import filter_tweets, capture_groups, lowercase_array
from master_helpers import get_winner_helper, get_presenters_helper
from presenter_experimenting import presenter_experimenting


def winner_get(award_names, year):

    tweets = load_tweets(f'../data/gg{year}.json')

    # Use regex to filter the above tweets about the award to those that only mention a winner
    possible_winning_tweets = filter_tweets(
        tweets, ["w(ins|inner|inners|on|\s)", "receiv(es|ed|)", "(goes|went to)"], _or=True)

    # exlude terms that don't imply a winner (negations, hope, should, etc.)
    winner_tweets = filter_tweets(possible_winning_tweets, [
                                  "(should(\'ve| have)\s),(did(n\'t| not)\s),(hop(e|ing))"], exclude=True, _or=True)

    to_return = {}
    # for each award
    for idx, award in enumerate(award_names):
        # call function to do all the work, passing in specific regex to use
        # try specific approach for Best Screenplay - Motion Picture and best original song - motion picture
        if award.lower() in ['best screenplay - motion picture', 'best original song - motion picture']:
            winner = get_winner_helper(
                winner_tweets, award.lower(), [('(.*)(goes|went) to (.*)for(.*?)', -1), ('(.*)(wins|won|receives)(.*)for(.*?)', -1), ('(.*)by(.*)', 0), ('(wins|won|receives)', 0), ('(goes|went) to', -1), ('winne(r|rs) (is|are)', -1)])
        else:
            winner = get_winner_helper(
                winner_tweets, award.lower(), [('(wins|won|receives)', 0), ('(goes|went) to', -1), ('winne(r|rs) (is|are)', -1), ('winner, (.*) is', -1)])

        # winner is the candidate with most occurences
        try:
            winner1 = list(winner.keys())[0]
        # if no candidates, no winner
        except Exception as e:
            winner1 = None
        # append winner to master list
        to_return[award] = winner1

    # return master list
    return(to_return)


def presenters_get(award_names, year):
    tweets = load_tweets(f'../data/gg{year}.json')

    # Use regex to filter the above tweets about the award to those that only mention a presenter
    possible_presenter_tweets = filter_tweets(
        tweets, ["presen(ts|ter|ters|ted|ting|ta)"], _or=True)

    to_return = {}
    # for each award, pass in the regex combo we are looking for
    for idx, award in enumerate(award_names):
        percents_dict = get_presenters_helper(
            possible_presenter_tweets, award, [('present(s|ed)', 0), ('presenting (.*) (is|are)', -1), ('presenting', 0)])
        # add candidates and count to return dict to filter more later
        to_return[award] = (percents_dict)
    # return master dict of dicts
    return(to_return)


def finalize_presenters(winners, presenters):
    to_return = {}
    # for each winner
    for award in winners.keys():
        potentials = {}
        winner = winners[award]
        # if no winner predicted, use empty string
        if not winner:
            winner = ''
        potential_presenters = presenters[award]
        # if we have potential presenters
        if potential_presenters:
            for pp in potential_presenters.keys():
                # if the potential presenter is not the winner add to potentials
                if Levenshtein.ratio(winner.lower(), pp.lower()) < 0.75:
                    potentials[pp] = potential_presenters[pp]
            # initlize list and refernce percent to 100%
            presenters_to_return = []
            percent = 1.0
            # for each candidate to return (not the award dinner)
            for key, value in potentials.items():
                # if no one in the list yet, add the top candidate and occurence %
                if len(presenters_to_return) == 0:
                    presenters_to_return.append(key)
                    if value > 0.65:
                        break
                    percent = value
                # if the second candidate is within 30% of the first, include
                else:
                    if percent - value < 0.3:
                        presenters_to_return.append(key)
                if len(presenters_to_return) == 2:
                    break
            # add the presenters to the master list
            to_return[award] = presenters_to_return
        else:
            # if no candidates, add an empty list
            to_return[award] = []
    # return master list
    return(to_return)


# if __name__ == "__main__":

#     OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
#                             'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

# # read in the tweets
# tweets13 = load_tweets('../data/gg2013.json')
# print(len(tweets13))
# # get the predicted winners passing award names and tweets
# predicted_winners = winner_get(OFFICIAL_AWARDS_1315, tweets13)
# # get the initial predicted presenters
# # predicted_presenters = get_presenters(OFFICIAL_AWARDS_1315, '2013')
# # use winners to further filter the predicted presenters
# # predicted_presenters2 = finalize_presenters(
# #     predicted_winners, predicted_presenters)
# print(predicted_winners)
