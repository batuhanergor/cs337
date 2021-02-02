import numpy as np
import pandas as pd
import re
import Levenshtein
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


def regex_filter(tweets, start, end):
    to_return = []
    for tweet in tweets:
        x = re.search(fr'{start}\.(.*?){end}', tweet.lower())
        if x:
            to_return.append(x)


def remove_part_of_tweet(tweets, to_exclude):
    df = pd.DataFrame(data={'text': tweets})
    for phrase in to_exclude:
        df['text'] = df['text'].str.replace(phrase, '')
    return(np.array(df['text']))


def levenshtein_dict(input_dict, thresh):
    to_return = {}
    sorted_dict = {k: v for k, v in sorted(
        input_dict.items(), key=lambda item: item[1], reverse=True)}
    for key in sorted_dict:
        to_add = True
        for key2 in to_return.keys():
            if Levenshtein.ratio(key2, key) > thresh:
                to_return[key2] += sorted_dict[key]
                to_add = False
        if to_add:
            to_return[key] = sorted_dict[key]
    return({k: v for k, v in sorted(
        to_return.items(), key=lambda item: item[1], reverse=True)})


def get_consecutive_pos(tweets, pos):
    to_return = []
    for tweet in tweets:
        poss = nltk.pos_tag(nltk.word_tokenize(tweet))
        consecutive_poss = []
        temp = []
        for entry in poss:
            if entry[1] == pos:
                temp.append(entry[0])
            else:
                if temp != []:
                    consecutive_poss.append(' '.join(temp))
                temp = []
        if temp != []:
            consecutive_poss.append(' '.join(temp))
        to_return.extend(consecutive_poss)
    return(to_return)


def clean(inputs, to_clean):
    to_return = []
    for phrase in inputs:
        keep = True
        for item in to_clean:
            if item in phrase:
                keep = False
        if keep:
            to_return.append(phrase)
    return(to_return)

def clean2(inputs, to_clean):
    return [phrase for phrase in inputs if not any(item in phrase for item in to_clean)]


def exclude_award_name(inputs, award):
    to_return = []
    for phrase in inputs:
        if phrase.lower() not in award.lower():
            to_return.append(phrase)
    return(to_return)

def exclude_award_name2(inputs, award):
    return [phrase for phrase in inputs if phrase.lower() not in award.lower()]