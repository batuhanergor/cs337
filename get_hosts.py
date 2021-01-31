from filter_tweets import filter_tweets, capture_groups
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re

tweets = load_tweets('gg2013.json')
host_tweets = filter_tweets(tweets, "host(s|ed|ing|)\s")
host_tweets = filter_tweets(host_tweets, "(should(\'ve| have)\s)", exclude=True)
cg = capture_groups(host_tweets, "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+))")
values, counts = np.unique(cg, return_counts=True)
print(values[np.argsort(counts)])
# print(cg)