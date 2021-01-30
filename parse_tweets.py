import pandas as pd
import numpy as np
import nltk
from load_tweets_and_answers import load_tweets, load_answers


def keyword_filter(file, keywords=[]):
    all_tweets = pd.DataFrame(load_tweets(file))
    to_returns = pr.DataFrame([])
    for keyword in keywords:
        to_return = to_return.append(all_tweets[all_tweets['text'].str.lower(
        ).str.contains(keyword)])
    return(to_return)


if __name__ == "__main__":
    get_hosts('data/gg2013.json')
    # print(hosts)
