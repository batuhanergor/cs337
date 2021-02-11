from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import get_consecutive_pos, clean2, clean
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import time

def num_hosts(sorted_counts):
    ''' 
        Returns expected number of hosts based on simple algorithm.
    '''
    return 2 if sorted_counts[-2] >= sorted_counts[-1] - sorted_counts[-1]*0.2 else 1

def get_hosts(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    host_tweets = filter_tweets(tweets, ["host(s|ed|ing|\s|)"])
    host_tweets = filter_tweets(host_tweets, ["(should(\'ve| have)\s)","next"], exclude=True, _or=True)
    cg = capture_groups(host_tweets, "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+))")
    cg = filter_tweets(cg, ["Golden Globes"], exclude=True, _or=True)
    values, counts = np.unique(cg, return_counts=True)
    nh = num_hosts(np.sort(counts))
    return np.sort(np.char.lower(values[np.argsort(counts)][-nh:]))

def get_hosts2(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    host_tweets = filter_tweets(tweets, ["host(s|ed|ing|\s|)"])
    host_tweets = filter_tweets(host_tweets, ["(should(\'ve| have)\s)","next", "rt"], exclude=True, _or=True)
    cg = np.array(get_consecutive_pos(host_tweets, 'NNP'))
    cg = np.array(clean2(cg, ['RT', '@', 'Golden', 'Globe', 'Award', '#']))
    values, counts = np.unique(cg, return_counts=True)
    nh = num_hosts(np.sort(counts))
    return np.sort(np.char.lower(values[np.argsort(counts)][-nh:]))

print(f'Answers: {load_answers("../data/gg2015answers.json")["hosts"]}')
t = time.time()
print(f'Results: {get_hosts("2015")} in {time.time() - t}')
t = time.time()
print(f'Results: {get_hosts2("2015")} in {time.time() - t}')