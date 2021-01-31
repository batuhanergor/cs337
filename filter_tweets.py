import numpy as np
import re

def filter_tweets(tweets, pats, exclude=False):
    ''' 
        Returns a numpy array of all tweets including (or excluding) a list of patterns 
        *Note*: Order of patterns matters!
    '''
    for p in pats:
        tweets = tweets[np.vectorize(lambda x: re.search(p, x) == None if exclude else re.search(p, x) != None)(tweets)]
    return tweets

def capture_groups(tweets, pat):
    ''' 
        Returns a numpy array of the capture groups
        in each tweet using a pattern 
    '''
    return np.concatenate([re.findall(pat, x) for x in tweets]).flatten()

def lowercase_array(arr):
    return np.array([str.lower() for str in arr])