import numpy as np
import pandas as pd
import re
import Levenshtein
import nltk
import itertools
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


def keyword_filter(df, keywords=[], method='or'):
    df = pd.DataFrame(data={'text': df})
    to_return = pd.DataFrame([])
    if method == 'or':
        for keyword in keywords:
            to_return = to_return.append(df[df['text'].str.lower(
            ).str.contains(keyword)])
    if method == 'and':
        to_return = df.copy(deep=True)
        for keyword in keywords:
            to_return = to_return[to_return['text'].str.lower(
            ).str.contains(keyword)]
    return(to_return)


def regex_filter(tweets, start, end):
    to_return = []
    for tweet in tweets:
        x = re.search(fr'{start}(.*?){end}', tweet.lower())
        if x:
            to_return.append(x)


def leave_one_out(input_list):
    subsets = []
    for i in range(len(input_list)):
        subsets.append(input_list[:i] + input_list[i+1:])
    return(subsets)


def get_combinations(input_list, n):
    return(itertools.combinations(input_list, n))


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
            if Levenshtein.ratio(key2.lower(), key.lower()) > thresh:
                to_return[key2] += sorted_dict[key]
                to_add = False
        if to_add:
            to_return[key] = sorted_dict[key]
    return({k: v for k, v in sorted(
        to_return.items(), key=lambda item: item[1], reverse=True)})


def split_on(input_list, term, index_to_take):
    to_return = []
    for x in input_list:
        if term.lower() in x.lower():
            to_return.append(x.split(term)[index_to_take])
        else:
            to_return.append(x)
    return(to_return)


def match_subsets(input_dict):
    to_return = {}
    to_remove = []
    total = sum([v for k, v in input_dict.items()])
    sorted_dict = {k: v for k, v in sorted(
        input_dict.items(), key=lambda item: item[1], reverse=True)}
    for key in sorted_dict:
        to_add = True
        value_to_add = sorted_dict[key]
        for key2 in to_return.keys():
            if key2.replace(' ','') in key.replace(' ','') and (sorted_dict[key]/total > 0.10 or (sorted_dict[key] > 100 and sorted_dict[key]/total > 0.05)):
                # and sorted_dict[key] > 3:
                value_to_add += sorted_dict[key2]
                to_remove.append(key2)
            elif key.replace(' ','') in key2.replace(' ',''):
                to_return[key2] += sorted_dict[key]
                to_add = False
        if to_add:
            to_return[key] = value_to_add
    for x in list(set(to_remove)):
        del to_return[x]
    total = sum([v for k, v in to_return.items()])
    return({k: v for k, v in sorted(
        to_return.items(), key=lambda item: item[1], reverse=True)}, {k: v/total for k, v in sorted(
            to_return.items(), key=lambda item: item[1], reverse=True)})


def get_consecutive_pos(tweets, pos):
    to_return = []
    for tweet in tweets:
        # for word in tweet.split(' '):
            # if len(word) > 0 and word[0] == '"':
            #    to_return.append(word.replace('"', ''))
            #    tweet.replace(word, '')
        tweet.replace('!', '').replace(
            '*', '').replace('"', '').replace("'", '')
        tweet_cleaned = tweet
        poss = nltk.pos_tag(nltk.word_tokenize(tweet_cleaned))
        consecutive_poss = []
        temp = []
        for entry in poss:
            if entry[0] == ')':
                consecutive_poss = []
                temp = []
                continue
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


def groups_around_regex(tweets, regex, position_to_take):
    winners = []
    for tweet in tweets:
        m = re.match(rf"(.*){regex}(.*)", tweet, flags=re.I)
        if m:
            winners.append(m.groups()[position_to_take])
    return(winners)


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


def exclude_award_name(inputs, award):
    to_return = []
    for phrase in inputs:
        if phrase.lower() not in award.lower():
            to_return.append(phrase)
    return(to_return)


def clean_based_on_award_recipient(tweets, award_name):
    df = pd.DataFrame(data={'text': tweets})
    if 'actor' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('actor')]
    elif 'actress' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('actress')]
    elif 'director' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('director')]
    elif 'song' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('song')]
    elif 'score' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('score')]
    else:
        pass
    if 'actor' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('actor')]
    if 'actress' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('actress')]
    if 'director' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('director')]
    if 'song' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('song')]
    if 'score' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('score')]
    return(df['text'])


def clean_based_on_award_recipient2(award_pos, award_name):
    to_return = award_pos
    if 'actor' in award_name.lower():
        to_return = [x for x in to_return if 'actor' in ' '.join(x).lower()]
    elif 'actress' in award_name.lower():
        to_return = [x for x in to_return if 'actress' in ' '.join(x).lower()]
    elif 'director' in award_name.lower():
        to_return = [x for x in to_return if 'director' in ' '.join(x).lower()]
    elif 'song' in award_name.lower():
        to_return = [x for x in to_return if 'song' in ' '.join(x).lower()]
    elif 'score' in award_name.lower():
        to_return = [x for x in to_return if 'score' in ' '.join(x).lower()]
    else:
        pass
    return(to_return)


def clean_based_on_award_subject(tweets, award_name):
    df = pd.DataFrame(data={'text': tweets})
    if 'motion picture' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('motion picture')]
    elif 'series' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('series')]
    elif 'television' in award_name.lower():
        df = df[(df['text'].str.lower().str.contains('television')) |
                (df['text'].str.lower().str.contains('tv'))]
    else:
        pass
    if 'motion picture' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('motion picture')]
    if 'series' not in award_name.lower():
        df = df[~df['text'].str.lower().str.contains('series')]
    if 'television' not in award_name.lower():
        df = df[~(df['text'].str.lower().str.contains('television')) &
                ~(df['text'].str.lower().str.contains('tv'))]
    if 'comedy' not in award_name.lower():
        df = df[~(df['text'].str.lower().str.contains('comedy'))]
    if 'drama' not in award_name.lower():
        df = df[~(df['text'].str.lower().str.contains('drama'))]
    if 'musical' not in award_name.lower():
        df = df[~(df['text'].str.lower().str.contains('musical'))]
    if 'supporting' in award_name.lower():
        df = df[df['text'].str.lower().str.contains('supporting')]
    return(df['text'])


def clean_based_on_award_subject2(award_pos, award_name):
    to_return = award_pos
    if 'motion picture' in award_name.lower():
        to_return = [
            x for x in to_return if 'motion picture' in ' '.join(x).lower()]
    elif 'series' in award_name.lower():
        to_return = [x for x in to_return if 'series' in ' '.join(x).lower()]
    elif 'television' in award_name.lower():
        to_return = [x for x in to_return if 'television' in ' '.join(x)]
    else:
        pass
    return(to_return)


def made_for_tv(tweets, award):
    df = pd.DataFrame(data={'text': tweets})
    if 'made for television' in award.lower():
        df = df[((df['text'].str.lower().str.contains('for television')) |
                 ((df['text'].str.lower().str.contains('for tv')))) & (~df['text'].str.contains('motion picture'))]
    return(df['text'])


def check_answer(answers, award, category, value):
    return(value.lower() == answers[award][category].lower())


def get_pos(df, pos):
    to_return = []
    for _, row in df.iterrows():
        tags = nltk.pos_tag(nltk.word_tokenize(
            re.sub('[^A-Za-z ]+', '', row['text'])))
        proper_nouns = [x[0] for x in tags if x[1] == pos and x[0].lower() not in (
            ['golden', 'globes', 'goldenglobes', 'rt'])]
        to_return.extend(proper_nouns)
    return(to_return)


def get_top_k(input_list, k):
    elements, counts = np.unique(input_list, return_counts=True)
    zipped = list(zip(elements, counts))
    ordered = sorted(zipped, key=lambda x: x[1], reverse=True)
    return(ordered[:k])


def handle_hashtags(input_list):
    to_return = []
    for entry in input_list:
        for term in entry.split(' '):
            term = term.strip(' ')
            if len(term) > 0 and term[0] == '#':
                to_return.append(
                    ' '.join(re.findall('[A-Z0-9][^A-Z]*', term[1:])))
    return(to_return)


def handle_handles(input_list):
    to_return = []
    for entry in input_list:
        is_rt = False
        for term in entry.split(' '):
            term = term.strip(' .')
            if is_rt:
                is_rt = False
                continue
            if term == 'RT':
                is_rt = True
                continue
            else:
                is_rt = False
                if len(term) > 0 and term[0] == '@':
                    to_return.append(
                        ' '.join(re.findall('[A-Z][^A-Z]*', term.strip(' @_*&^%$!'))))
    return(to_return)
