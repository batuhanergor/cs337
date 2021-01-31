from filter_tweets import filter_tweets, capture_groups
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re

tweets = load_tweets('gg2013.json')
host_tweets = filter_tweets(tweets, "host(s|ed|ing|)\s")
tw = host_tweets[np.vectorize(lambda x: "Amy Poehler" in x and "Tiny Fey" in x)(host_tweets)]

my_str = "Tiny Fey and Amy Poehler are hosting the Golden Globes!"
lst = np.array(["Tiny Fey and Amy Poehler are hosting the Golden Globes!", "I ate a pig named Stu", "Apple Pie is delicious", "Hello World", "beep boop"])
b = capture_groups(lst, "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)")
print(b)
a = re.findall("([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)", my_str)
print(a)