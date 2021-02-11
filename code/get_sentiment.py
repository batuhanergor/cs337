from filter_tweets import filter_tweets, capture_groups
from helper_funcs import get_consecutive_pos, clean2
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re
import nltk
import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
# nltk.download('stopwords')

def load_tweets2(filename):
    return pd.read_json(filename)
    
def best_dressed(tweets):
    best_dressed = filter_tweets(tweets, ['(?i)best dressed'])
    best_dressed = np.random.choice(best_dressed, sample_size(len(best_dressed), 0.5, 0.01, 2.58), replace=False)
    best_dressed = np.char.lower(np.array(get_consecutive_pos(best_dressed, 'NNP')))
    best_dressed = np.array(clean2(best_dressed, ['rt', '@', 'golden', 'globe', 'award', '#', 'best', 'red carpet','damn','eredcarpet','redcarpet']))
    best_dressed = np.array([remove_emojis(x) for x in best_dressed])
    values, counts = np.unique(best_dressed, return_counts=True)
    bd = values[np.argsort(counts)][-1]
    print(f'Best Dressed: {" ".join(w.capitalize() for w in bd.split())}')
    # for i, b in enumerate(bd):
    #     print(f'{i+1}. {" ".join(w.capitalize() for w in b.split())}')

def worst_dressed(tweets):
    worst_dressed = filter_tweets(tweets, ['(?i)worst dressed'])
    worst_dressed = np.random.choice(worst_dressed, sample_size(len(worst_dressed), 0.5, 0.01, 2.58), replace=False)
    worst_dressed = np.char.lower(np.array(get_consecutive_pos(worst_dressed, 'NNP')))
    worst_dressed = np.array(clean2(worst_dressed, ['rt', '@', 'golden', 'globe', 'award', 'goldenglobe' '#', 'worst', 'wtf', 'red carpet','damn','eredcarpet','redcarpet']))
    worst_dressed = np.array([remove_emojis(x) for x in worst_dressed])
    values, counts = np.unique(worst_dressed, return_counts=True)
    bd = values[np.argsort(counts)][-1]
    x = dict(zip(values, counts))
    print(f'Worst Dressed: {" ".join(w.capitalize() for w in bd.split())}')
    # for i, b in enumerate(bd):
    #     print(f'{i+1}. {" ".join(w.capitalize() for w in b.split())}')


def most_discussed(tweets):
    most_discussed= filter_tweets(tweets, ['(?i)red carpet|redcarpet'])
    most_discussed = np.random.choice(most_discussed, sample_size(len(most_discussed), 0.5, 0.01, 2.58), replace=False)
    # most_discussed = filter_tweets(most_discussed, ['(?i)rt'], exclude=True)
    # cg = capture_groups(worst_dressed, "([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+))")
    # worst_dressed = filter_tweets(cg, ["Golden Globes"], exclude=True, _or=True)
    most_discussed = np.char.lower(np.array(get_consecutive_pos(most_discussed, 'NNP')))
    most_discussed = np.array(clean2(most_discussed, ['rt', '@', 'golden', 'globe', 'award', '#', 'worst', 'redcarpet','eredcarpet','red carpet','red']))
    # worst_dressed = np.array([remove_emojis(x) for x in worst_dressed])
    values, counts = np.unique(most_discussed, return_counts=True)
    # x = dict(zip(values, counts))
    # print({k: v for k, v in sorted(x.items(), key=lambda item: item[1])})
    bd = values[np.argsort(counts)][-1]
    # x = dict(zip(values, counts))
    print(f'Most Discussed: {" ".join(w.capitalize() for w in bd.split())}')
    # for i, b in enumerate(bd):
    #     print(f'{i+1}. {" ".join(w.capitalize() for w in b.split())}')

def sample_size(pop, cl, err, z):
    num = (z**2 * cl*(1-cl)) / (err**2)
    denom = 1 + ( (z**2 * cl*(1-cl)) / (err**2 * pop) )
    ss = round(num/denom)
    print(ss)
    return ss

def get_sentiment(tweets, people):
    host_tweets = filter_tweets(tweets, ['(?i)'+' | '.join(people)])
    sentiment = np.array([TextBlob(x).sentiment.polarity for x in host_tweets]).mean()
    print(sentiment)
    # df.text = df.text.map(lambda x: re.sub("(?i)best", '', x))
    # groups = df.groupby(df.timestamp_ms.dt.floor('15min')).indices
    # sentiments = []g
    # # baw = []
    # for x in groups:
    #     sentiments.append(df[df.index.isin(groups[x])].text.map(lambda x: TextBlob(x).sentiment.polarity).mean())
    #     # baw.append(df[df.index.isin(groups[x])].text.map(lambda x: [word for word in word_tokenize(x) if not word in stopwords.words()]))
    # print(sentiments)


def extras(year):
    total = time.time()
    tweets = load_tweets(f'../data/gg{year}.json')
    hosts = load_answers(f'../data/gg{year}answers.json')['hosts']
    print('Getting best dressed...')
    t = time.time()
    best_dressed(tweets)
    print(f'Got best dressed in {time.time() - t} seconds.\n')

    print('Getting worst dressed...')
    t = time.time()
    worst_dressed(tweets)
    print(f'Got worst dressed in {time.time() - t} seconds.\n')

    print('Getting most discussed...')
    t = time.time()
    most_discussed(tweets)
    print(f'Got most discussed in {time.time() - t} seconds.\n')

    print(f'Total time: {time.time() - total}')
    # print('Getting host sentiment...')
    # t = time.time()
    # get_sentiment(tweets, hosts)
    # print(f'Got host sentiment in {time.time() - t} seconds.\n')

def remove_emojis(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)
    
extras(2013)
extras(2015)

# df = get_sentiment(0)
# df.text = df.text.map(lambda x: re.sub("(?i)best", '', x))
# groups = df.groupby(df.timestamp_ms.dt.floor('15min')).indices
# for x in groups:
#     print(len(groups[x]))
#     print(df[df.index.isin(groups[x])].text.map(lambda x: TextBlob(x).sentiment.polarity).mean())
#     # print(df[df.index.isin(groups[x])])
