import numpy as np
import re

def filter_tweets(tweets, pat):
    ''' 
        Returns a numpy array of all tweets containing a pattern 
    '''
    return tweets[np.vectorize(lambda x: re.search(pat, x) != None)(tweets)]

def capture_groups(tweets, pat):
    ''' 
        Returns a numpy array of the capture groups
        in each tweet using a pattern 
    '''
    return np.concatenate([re.findall(pat, x) for x in tweets]).flatten()