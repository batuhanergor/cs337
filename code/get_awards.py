from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import clean2, get_consecutive_pos
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re
from fuzzywuzzy import fuzz
import nltk
from spellchecker import SpellChecker


def get_awards(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    print(f'There are {len(tweets)} total tweets.')
    award_tweets = filter_tweets(tweets, ['(?i)rt\s','[Dd](ress|ressed)','(?i)(ever|worst|moment|moments|insults|jokes|insult|joke)'], exclude=True, _or=True)
    award_tweets = filter_tweets(award_tweets, ['(?i)best'])
    cg2 = capture_groups(award_tweets, "(?i)(?:wins\s)(?:(best\s(.*?))(?=\shttp|\sto|\sand|\sat|(?!\smade)\sfor|\swinner|\sis|\sat|[.!?$:|#@]|\swell|\swith|\s\"|\sgolden|\sglobe|\s\(|\s[0-9+]|\sand|\saward))")
    cg2 = np.array([s for s in cg2 if s.startswith('best')]) #re.search('(?i)best', s)])
    all_cg = np.char.lower(cg2)
    all_cg = filter_tweets(all_cg, ['best of','who','the','\si\s','(?i)i\'m'], exclude=True, _or=True)
    all_cg = [a for a in np.unique([b.rstrip() for b in all_cg]) if len(a.split())>1]
    test = all_cg
    test = np.array(list(map(lambda s: award_process(s), test)))
    fuzzy_dict = fuzzyRatio(test, 90)
    print({k: v for k, v in sorted(fuzzy_dict.items(), key=lambda item: item[1])})
    ret = np.array([k for k,v in fuzzy_dict.items() if v>5])
    ret = spell_checker(ret)
    ret = remove_if_subset(ret)
    print(f'len before add: {len(ret)}')
    ret = add_awards(ret)
    ret = remove_if_subset(ret)
    # ret = spell_checker(ret)
    print(f'len after add: {len(ret)}')
    unique = np.unique(ret)
    print(unique)
    print(len(unique))

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
                        len(s2_split)-len(substr)<=3: #and \
                            #(('supporting' not in s2_split) or ('supporting' in s2_split and 'supporting' in substr)):
                    incl = False
                    break
        if incl: 
            ret.append(s)
    return np.array(ret)
    # return [s for s in strs if not any( all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s2) or sub=='or' for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s)) for s2 in strs if s!=s2)]

def multi_sub(pairs, s):
    # ORDER MATTERS!
    new_s = s
    for p in pairs:
        new_s = re.sub(p[0], p[1], new_s)
    return new_s.split()

# TODO: replace 'show' with 'series' 
#       replace 'movie' with 'motion picture'
#       just 'series' -> 'television series'
#       just 'television' -> 'television series'
def award_process(award):
    award = re.sub('best actor','best performance by an actor', award) #award.replace('best actor','best performance by an actor')
    award = re.sub('best actress','best performance by an actress', award)
    award = re.sub('supporting actor', 'performance by an actor in a supporting role', award)
    award = re.sub('supporting actress', 'performance by an actress in a supporting role', award)
    award = re.sub('(?i)tv', 'television', award)
    award = re.sub('show','series',award)
    award = re.sub('movie','motion picture',award)
    if 'series' in award and 'television' not in award:
        award = re.sub('series', 'television series', award)
    if 'television' in award and 'series' not in award:
        award = re.sub('television', 'television series', award)
    award = re.sub('minitelevision', 'mini-series television', award)
    award = re.sub('miniseries', 'mini-series', award)
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
            
            # if all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], c) for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], other)):
            #     d[c]+=1
            # if all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], other) for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], c)):
            #     d[other]+=1

            # subst = remove_if_subset([c,other])
            # if len(subst) != 0:
            #     if c in subst: d[c]+=1
            #     if other in subst: d[other]+=1
            # else:
            #     d[c]+=1
            #     d[other]+=1
            # if len(remove_if_subset([c,other])) in [0,1] and c!=other:
            #     # print(f'c:{c}\tother:{other}')
            #     d[c]+=1
            #     d[other]+=1
    return d

res = get_awards("2015")

# test = np.array(['best animated feature', 'best motion picture drama',
#  'best performance by an actor in a minitelevision series',
#  'best performance by an actor in a supporting role in a miniseries or television motion picture',
#  'best performance by an actor in a supporting role in a television series',
#  'best performance by an actor in a television series comedy/musical',
#  'best performance by an actress in a mini-television series',
#  'best performance by an actress in a motion picture comedy/musical',
#  'best performance by an actress in a motion picture drama',
#  'best performance by an actress in a supporting role in a television series, miniseries or motion picture',
#  'best performance by an actress in a television drama',
#  'best performance by an actress in a television series comedy/musical',
#  'best performance by an actress in minitelevision series',
#  'best performance by an actress mini-series, television motion picture',
#  'best screenplay, motion picture' 'best television series comedy/musical',
#  'best television series dram'])
# for a in test:
#     x = re.search('(?!supporting role)(?<=in a ).*',a)
#     if x: print(x.group(0))

# s = ['best performance by an actress in a television drama','best performance by an actress--television drama']
# ret = remove_if_subset(s)
# print(ret)
# s = ['best performance by an actor comedy/musical', 'best performance by an actor in a comedy/musical']
# sub = re.sub("[^\w\s\/]+", '', s[0])#.split()
# sub = re.sub("[\/.,-]", ' ', sub).split()
# print(sub)
# if all(sb in s[1] for sb in sub):
#     print('ALL IN!')
# else: print('NOT ALL IN!')
# for sb in sub:
    # print(f'{sb} {sb in s[1]}')
# print(f'test: is best in \'best performance\': {"best" in "best performance by an actor in a comedy/musical"}')
# s = 'best performance by an actress in television comedy'
# sub = re.sub("[^\w\s]+", '', s).split()
# print(sub)
# ans = load_answers("../data/gg2015answers.json")["awards"]
# # print(res)
# # print(len(res))
# a=[b for b in res if not any(b in c for c in res if b!=c)]
# print(len(a))
# # for b in res:
# #     if not any(b in c for c in res if b!=c):
# #         a.append(b)
# fuzzy_dict = fuzzyRatio(a, 90, lessThan=False)
# ret = np.array([k for k,v in fuzzy_dict.items() if v>5])
# ret = [b for b in ret if not any(b in c for c in ret if b!=c)]
# print(ret)
# print(len(ret))
# print(f'Answers: {ans}\n\n')
# for an in ans:
#     print(f'{an}')
# print(f'\n\nResults: {res}\nLength: {len(res)}\nUnique: {len(np.unique(res))}\n\n')
# unique, counts = np.unique(res, return_counts=True)
# print(unique[np.where(counts>5)])
# res1 = unique[np.where(counts>5)]
# a = [b for b in res1 if b in ans]
# # print(f'{a}\n\n')
# unique, counts = np.unique(a,return_counts=True)
# # print(list(zip(unique,counts)))
# print(f"found exact match for {len(unique)} / {len(ans)} in {np.sum(counts)} tweets")

## testing:
# s1 = "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television"
# s2 = "best performance by an actor in a television series - comedy or musical"
# pos = [nltk.pos_tag(nltk.word_tokenize(name)) for name in ans]
# lst = []
# lst2 = []
# for i in range(len(max(pos, key=len))):
#     inner = []
#     inner2 = []
#     for p in pos:
#         if i<len(p):
#             inner.append(p[i][1])
#             inner2.append(p[i][0])
#     lst.append(inner)
#     lst2.append(inner2)
# lst_unique = np.array([np.array(np.unique(l)) for l in lst], dtype=object)
# lst_unique2 = np.array([np.array(np.unique(l)) for l in lst2], dtype=object)
# # print(lst_unique)
# # print(lst_unique2)
# print(nltk.pos_tag(nltk.word_tokenize('cecil b. demille award')))
# for k in range(len(lst_unique)):
#     print(f'{lst_unique[k]}\n{lst_unique2[k]}\n\n')


# b = [array(['JJS', 'NN', 'RB', 'RBS'], dtype='<U3')
#  array(['JJ', 'NN', 'NNS', 'VBN'], dtype='<U3')
#  array([':', 'CC', 'IN', 'NN', 'VBZ'], dtype='<U3')
#  array([':', 'DT', 'NN'], dtype='<U2') array(['NN'], dtype='<U2')
#  array(['CC', 'IN', 'NN', 'VBN'], dtype='<U3')
#  array(['DT', 'IN', 'JJ'], dtype='<U2')
#  array(['JJ', 'NN', 'NNS'], dtype='<U3') array(['CC', 'NN'], dtype='<U2')
#  array([':', 'IN', 'NN'], dtype='<U2') array(['DT', 'NN'], dtype='<U2')
#  array(['CC', 'NN', 'VBN'], dtype='<U3')
#  array([',', 'IN', 'JJ', 'NN'], dtype='<U2')
#  array(['NN', 'NNS'], dtype='<U3') array(['CC'], dtype='<U2')
#  array(['NN'], dtype='<U2') array(['NN'], dtype='<U2')
#  array(['VBN'], dtype='<U3') array(['IN'], dtype='<U2')
#  array(['NN'], dtype='<U2')]

#  a = [  ['JJS', 'NN', 'RB', 'RBS'], # best
#     ['JJ', 'NN', 'NNS', 'VBN'], # director / performance / foreign /
#     [':', 'CC', 'IN', 'NN', 'VBZ'],
#     [':', 'DT', 'NN'],
#     ['NN'],
#     ['CC', 'IN', 'NN', 'VBN'],
#     ['DT', 'IN', 'JJ'],
#     ['JJ', 'NN', 'NNS'],
#     ['CC', 'NN'],
#     [':', 'IN', 'NN'],
#     ['DT', 'NN'],
#     ['CC', 'NN', 'VBN'],
#     [',', 'IN', 'JJ', 'NN'],
#     ['NN', 'NNS'],
#     ['CC'],
#     ['NN'],
#     ['NN'],
#     ['VBN'],
#     ['IN'],
#     ['NN']
# ]

# c = ['best', 
#     ['JJ', 'NNS', 'VBN', 'NN'],
#     [':' 'CC' 'IN' 'NN' 'VBZ']]
#     ['NN'],

# def award_process(award):
#     award = award.replace('best actor','best performance by an actor')
#     award = award.replace('best actress','best performance by an actress')
#     award = award.replace('supporting actor', 'performance by an actor in a supporting role')
#     award = award.replace('supporting actress', 'performance by an actress in a supporting role')
#     if sum(1 for _ in re.finditer(',\s', award)) == 1 and not re.search('\sor\s', award):
#         award = award.replace(',\s', ' or ')
#     if re.search('(drama)', award):
#         award = award.replace('(drama)','drama')
#     if re.search('drama', award):
#         award = award.split('drama')[0]+'drama'
#     if not re.search('\sin a\s', award) and award.endswith('motion picture') and not re.search('- motion picture', award):
#         award = award.replace('motion picture', '- motion picture')
#     if award.endswith('drama') and not re.search('- drama', award):
#         award = award.replace('drama', '- drama')
#     award = award.replace('tv','television')
#     award = award.replace('telelvision','television')
#     if re.search('picture', award) and not re.search('motion picture', award):
#         award = award.replace('picture', 'motion picture')
#     if re.search('comedy/musical', award):
#         award = award.replace('comedy/musical', 'comedy or musical')
#     if re.search('comedy', award) and not re.search('musical', award):
#         award = award.replace('comedy', 'comedy or musical')
#     if award.endswith('comedy or musical') and not re.search('- comedy or musical', award):
#         award = award.replace('comedy or musical', '- comedy or musical')
#     if re.search('- - drama', award):
#         award = award.replace('- - drama','- drama')
#     if re.search(', - drama', award):
#         award = award.replace(', - drama', ' - drama')
#     if re.search(', motion picture', award):
#         award = award.replace(', motion picture', ' in a motion picture')
#     if re.search(', comedy or musical', award):
#         award.replace(', comedy or musical', ' - comedy or musical')
#     if re.search('roles', award):
#         award = award.replace('roles', 'role')
#     if re.search(', television series', award):
#         award = award.replace(', television series', ' in a television series')
#     return award