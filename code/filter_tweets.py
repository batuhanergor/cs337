import numpy as np
import re

def filter_tweets(tweets, pats, exclude=False, _or=False):
    ''' 
        Returns a numpy array of all tweets including (or excluding) a list of patterns.
        Note: if _or==True, exclude or include if *any* pattern present.
              if _or==False, exclude or include if *all* patterns present.
        **NOT CASE-SENSITIVE**
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

def capture_groups(tweets, pat):
    ''' 
        Returns a numpy array of the capture groups
        in each tweet using a pattern.
        **CASE-SENSITVE**
    '''
    return np.concatenate([np.array(re.findall(pat, x)).flatten() for x in tweets]).flatten()

def lowercase_array(arr):
    ''' 
        Makes all strings in numpy array lowercase.
    '''
    return np.array([str.lower() for str in arr])