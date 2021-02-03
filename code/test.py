import numpy as np
import re

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama',
                            'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

tweets = ["hi", "hi my name",  "'RT my name", "is", "Esther"]
tweets = np.asarray(tweets)

def filter_tweets(tweets, pats, exclude=False, _or=False):
    '''
        Returns a numpy array of all tweets including (or excluding) a list of patterns.
        Note: if _or==True, exclude or include if *any* pattern present.
              if _or==False, exclude or include if *all* patterns present.
    '''
    if exclude:
        if _or:
            return tweets[np.vectorize(lambda x: not any([re.search(r, x.lower()) != None for r in pats]))(tweets)]
        else:
            return tweets[np.vectorize(lambda x: not all([re.search(r, x.lower()) != None for r in pats]))(tweets)]
    else:
        if _or:
            return tweets[np.vectorize(lambda x: any([re.search(r, x.lower()) != None for r in pats]))(tweets)]
        else:
            return tweets[np.vectorize(lambda x: all([re.search(r, x.lower()) != None for r in pats]))(tweets)]

nominees_tweets2 = filter_tweets(tweets, ["\'RT"], exclude=True, _or=False)
#nominees_tweets2 = filter_tweets(nominees_tweets2, ["my"], exclude=True, _or=False)
print(nominees_tweets2)
