from filter_tweets import filter_tweets, capture_groups, lowercase_array
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re

def num_hosts(sorted_counts):
    return 2 if sorted_counts[-2] >= sorted_counts[-1] - sorted_counts[-1]*0.1 else 1

tweets = load_tweets('gg2013.json')
answers = load_answers('gg2013answers.json')
host_tweets = filter_tweets(tweets, ["host(s|ed|ing|)\s"])
host_tweets = filter_tweets(host_tweets, ["(should(\'ve| have)\s)","next"], exclude=True)
cg = capture_groups(host_tweets, "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+))")
values, counts = np.unique(np.array([x for x in cg if "Golden Globes" not in x]), return_counts=True)
# print(sorted(list(zip(values, counts)), key = lambda x: x[1]))

print(f'Answers: {answers["hosts"]}')
num_hosts = num_hosts(np.sort(counts))
print(f'Results: {np.sort(lowercase_array(values[np.argsort(counts)][-num_hosts:]))}')