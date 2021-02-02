from filter_tweets import filter_tweets, capture_groups, lowercase_array
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re

def get_awards(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    host_tweets = filter_tweets(tweets, ["(award\s|nominated\s|nomination\s|goes to\s)"])
    host_tweets = filter_tweets(host_tweets, ['rt\s'], exclude=True)
    print(len(host_tweets))
    print(host_tweets)
    cg = capture_groups(host_tweets, "[Bb]est ((.*?)(?=\sgoes to)|(?=[.!?]))")#"(best(?:[A-Za-z\s]+)(?!(goes to|[.?!])))") 
    # "(best\s(?:[A-Za-z\s]+)(?!(\s#|[.!?]|goes to)))" "(best(?:(.+?(?=(\sgoes|\sfor|[.?!])))))"
    print(cg)
    print(len(cg))

# print(f'Answers: {load_answers("../data/gg2013answers.json")["hosts"]}')
print(f'Results: {get_awards("2013")}')