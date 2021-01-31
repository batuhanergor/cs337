import numpy as np
import re

def filter_tweets(tweets, pats, exclude=False):
    ''' 
        Returns a numpy array of all tweets including (or excluding) a list of patterns.
    '''
    pat = '(' + '|'.join(map(str, pats)) +')'
    return tweets[np.vectorize(lambda x: re.search(pat, x.lower()) == None if exclude else re.search(pat, x.lower()) != None)(tweets)]

def capture_groups(tweets, pat):
    ''' 
        Returns a numpy array of the capture groups
        in each tweet using a pattern.
    '''
    return np.concatenate([re.findall(pat, x) for x in tweets]).flatten()

def lowercase_array(arr):
    ''' 
        Makes all strings in numpy array lowercase.
    '''
    return np.array([str.lower() for str in arr])