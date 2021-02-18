from filter_tweets import filter_tweets
from helper_funcs import get_consecutive_pos, clean
from load_tweets_and_answers import load_tweets
import numpy as np
import re
    
def best_dressed(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    best_dressed = filter_tweets(tweets, ['(?i)best dressed'])
    best_dressed = np.random.choice(best_dressed, sample_size(len(best_dressed), 0.5, 0.01, 2.58), replace=False)
    best_dressed = np.char.lower(np.array(get_consecutive_pos(best_dressed, 'NNP')))
    best_dressed = np.array(clean(best_dressed, ['rt', '@', 'golden', 'globe', 'goldenglobe', 'award', '#', 'best', 'red carpet','damn','eredcarpet','redcarpet']))
    best_dressed = np.array([remove_emojis(x) for x in best_dressed])
    values, counts = np.unique(best_dressed, return_counts=True)
    bd = values[np.argsort(counts)][-1]
    # print(f'Best Dressed: {" ".join(w.capitalize() for w in bd.split())}')
    return bd


def worst_dressed(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    worst_dressed = filter_tweets(tweets, ['(?i)worst dressed'])
    worst_dressed = np.random.choice(worst_dressed, sample_size(len(worst_dressed), 0.5, 0.01, 2.58), replace=False)
    worst_dressed = np.char.lower(np.array(get_consecutive_pos(worst_dressed, 'NNP')))
    worst_dressed = np.array(clean(worst_dressed, ['rt', 'best','photos','see', 'course', 'who','stars', '@', 'golden', 'globe', 'award', 'goldenglobe' '#', 'worst', 'wtf', 'red carpet','damn','eredcarpet','redcarpet']))
    worst_dressed = np.array([remove_emojis(x) for x in worst_dressed])
    values, counts = np.unique(worst_dressed, return_counts=True)
    wd = values[np.argsort(counts)][-1]
    # print(f'Worst Dressed: {" ".join(w.capitalize() for w in wd.split())}')
    return wd


def most_discussed(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    most_discussed= filter_tweets(tweets, ['(?i)red carpet|redcarpet'])
    most_discussed = np.random.choice(most_discussed, sample_size(len(most_discussed), 0.5, 0.01, 2.58), replace=False)
    most_discussed = np.char.lower(np.array(get_consecutive_pos(most_discussed, 'NNP')))
    most_discussed = np.array(clean(most_discussed, ['rt', '@', 'golden', 'globe', 'award', 'goldenglobe', '#', 'worst', 'redcarpet','eredcarpet','red carpet','red']))
    most_discussed = np.array([remove_emojis(x) for x in most_discussed])
    values, counts = np.unique(most_discussed, return_counts=True)
    md = values[np.argsort(counts)][-1]
    # print(f'Most Discussed: {" ".join(w.capitalize() for w in md.split())}')
    return md

def sample_size(pop, cl, err, z):
    num = (z**2 * cl*(1-cl)) / (err**2)
    denom = 1 + ( (z**2 * cl*(1-cl)) / (err**2 * pop) )
    return round(num/denom)

def remove_emojis(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

# worst_dressed('2013')
# s = 'Best Motion Picture Television Series Or Comedy Or Musical'
# print(len(re.findall('(?i) or ', s)))