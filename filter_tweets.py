import numpy as np

def filter_tweets(tweets, pat):
    ''' Returns a numpy array of all tweets containing a pattern '''
    return tweets[np.vectorize(lambda x: re.search(pat, x) != None)(tweets)]