from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import clean2, get_consecutive_pos
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re
from fuzzywuzzy import fuzz
import nltk
from spellchecker import SpellChecker
import time


def get_awards(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    # 2015: 1754153 
    # 2013: 0174643
    award_tweets = filter_tweets(tweets, ['(?i)rt\s','[Dd](ress|ressed)','(?i)(ever|worst|moment|moments|insults|jokes|insult|joke|presenter|recovery|pick|soundtrack|achievement|deserving|sex|picture)'], exclude=True, _or=True)
    award_tweets = filter_tweets(award_tweets, ['(?i)best'])
    cg2 = capture_groups(award_tweets, "(?i)(?:wins\s|won\s|nominated for\s|nominees for\s|nominations for\s)(?:(best\s(.*?))(?=\shttp|\sto|\sand|\sat|(?!\smade)\sfor|\swinner|\sis|\sat|[.!?$:|#@]|\swell|\swith|\s\"|\sgolden|\sglobe|\s\(|\s[0-9+]|\sand|\saward|\slol|\sright|\sare|\son|\sbut|,but|\sover|\sgo|\slast|\scamp\s|\smy|\swas|\sis|\sas|\sfirst|\sthat|\sof))")
    cg2 = np.array([s for s in cg2 if s.startswith('best')])
    all_cg = np.char.lower(cg2)
    all_cg = filter_tweets(all_cg, ['best of','who','the','\si\s','(?i)i\'m','after','camp','was','earlier','is','best picture','creator','mentioned','school','pick'], exclude=True, _or=True)
    all_cg = [a for a in np.unique([b.rstrip() for b in all_cg]) if len(a.split())>1]
    test = all_cg
    test = np.array(list(map(lambda s: award_process(s), test)))
    fuzzy_dict = fuzzyRatio(test, 90, lessThan=False)
    if (len(fuzzy_dict.keys()) > 150):
        ret = np.array([k for k,v in fuzzy_dict.items() if v>(round(max(fuzzy_dict.values()))*0.2)])
    else: 
        ret = np.array([k for k,v in fuzzy_dict.items()])
    ret = spell_checker(ret)
    ret = filter_tweets(ret, ['(?i)(season|that|so|featured|were|pick|school|both|categories|definitely|neck|go)'], exclude=True, _or=True)
    ret = split_take_first(ret, ' camp')
    ret = remove_after_word(ret, '(?i)^(.*?)(drama|musical)')
    ret = remove_if_subset(ret)
    ret = add_awards(ret)
    ret = remove_if_subset(ret)
    ret = remove_if_all_in(ret)
    ret = np.array(list(map(lambda s: award_process(s), ret)))
    unique = np.unique(ret)
    return unique

def split_take_first(arr, string):
    return np.array([a.split(string)[0] for a in arr])

def remove_after_word(arr, string):
    return np.array([re.search(string, a)[0] if re.search(string,a) else a for a in arr])

def spell_checker(arr):
    spell = SpellChecker()
    return np.array([' '.join([spell.correction(s) for s in string.split()]) for string in arr])

def add_awards(arr):
    ret = []
    for a in arr:
        x = re.search('(?!supporting role)(?<=in a ).*',a)
        if x: ret.append('best ' + x.group(0))
    return np.append(np.array(ret), arr)

def remove_if_subset(strs):
    ret = []
    for s in strs:
        substr = multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s)
        incl = True
        for s2 in strs:
            if s2!=s:
                s2_split = multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s2)
                if (all(sub in s2_split or sub=='or' for sub in substr) or s in s2) and \
                        len(s2_split)-len(substr)<=3 and\
                            (('supporting' not in s2_split) or ('supporting' in s2_split and 'supporting' in substr)):
                    incl = False
                    break
        if incl: 
            ret.append(s)
    return np.array(ret)

def remove_if_all_in(strs):
    ret = []
    for s in strs:
        incl = True
        for s2 in strs:
            if s2!=s:
                if all((sub in s2 and s.count(sub)<=s2.count(sub)) for sub in s) and len(s2.split())-len(s.split())<=2:
                    incl = False
                    break
        if incl: 
            ret.append(s)
    return np.array(ret)

def multi_sub(pairs, s):
    # ORDER MATTERS!
    new_s = s
    for p in pairs:
        new_s = re.sub(p[0], p[1], new_s)
    return new_s.split()

def award_process(award):
    award = re.sub('best actor','best performance by an actor', award)
    award = re.sub('best actress','best performance by an actress', award)
    award = re.sub('supporting actor', 'performance by an actor in a supporting role', award)
    award = re.sub('supporting actress', 'performance by an actress in a supporting role', award)
    award = re.sub('lead actress', 'actress', award)
    award = re.sub('female actress', 'actress', award)
    award = re.sub('lead actor', 'actor', award)
    award = re.sub('male actor', 'actor', award)
    award = re.sub('(?i)tv', 'television', award)
    award = re.sub('show','series',award)
    award = re.sub('movie','motion picture',award)
    if 'series' in award and 'television' not in award:
        award = re.sub('series', 'television series', award)
    if 'television' in award and 'series' not in award:
        award = re.sub('television', 'television series', award)
    award = re.sub('minitelevision', 'mini-series television', award)
    award = re.sub('miniseries', 'mini-series', award)
    if re.search('(?i)(comedy|comedic)', award) and not re.search('(?i)musical', award):
        award = re.sub('(?i)(comedy|comedic)', 'comedy or musical', award)
    if not re.search('(?i)(comedy|comedic)', award) and re.search('(?i)musical', award):
        award = re.sub('(?i)(musical)', 'comedy or musical', award)
    return award

def fuzzyRatio(cg, rat, lessThan=True):
    unique, counts = np.unique(cg, return_counts=True)
    d = {k:v for k,v in zip(unique, counts)}
    for c in d.keys():
        for other in d.keys():
            if fuzz.ratio(c, other) > rat:
                if lessThan:
                    if len(c)<len(other):
                        d[c] += 1
                    else: d[other] += 1
                else:
                    if len(c)>len(other):
                        d[c] += 1
                    else: d[other] += 1
            
            if all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], c) for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], other)):
                d[c]+=1
            if all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], other) for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], c)):
                d[other]+=1
    return d

t = time.time()
print('2015:')
res = get_awards("2015")
print(res)
print(len(res))
print(time.time() - t)

t = time.time()
print('2013')
res = get_awards("2013")
print(res)
print(len(res))
print(time.time() - t)