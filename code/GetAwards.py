import pandas as pd
import numpy as np
from load_tweets_and_answers import load_tweets, load_answers

if __name__ == "__main__":
    tweets = load_tweets('data/gg2013.json')
    print(tweets[:5])
