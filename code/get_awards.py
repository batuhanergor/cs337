from filter_tweets import filter_tweets, capture_groups, lowercase_array
from helper_funcs import clean2, get_consecutive_pos
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import re
from fuzzywuzzy import fuzz
import nltk

def get_awards2(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    # award_tweets = filter_tweets(tweets, ["(award for\s|nominated for\s|nomination for\s|goes to\s|winner of|won|wins|winning)"])
    award_tweets = filter_tweets(tweets, ['(?i)rt\s','[Dd](ress|ressed)','(?i)(ever|worst|moment|moments|insults|jokes|insult|joke)'], exclude=True, _or=True)
    award_tweets = filter_tweets(award_tweets, ['(?i)best'])
    # cg = capture_groups(award_tweets, "(?i)(best\s(.*?))(?:nominee|\sat||\sgoes to|\sto|\swinner|[.!?$:])")
    # cg = np.array([s for s in cg if s.startswith('best')])#re.search('(?i)best', s)])
    cg2 = capture_groups(award_tweets, "(?i)(?:wins\s)(?:(best\s(.*?))(?=\shttp|\sto|\sand|\sat|(?!\smade)\sfor|\swinner|\sis|\sat|[.!?$:|#@]|\swell|\swith|\s\"|\sgolden|\sglobe|\s\(|\s[0-9+]|\sand|\saward))")
    cg2 = np.array([s for s in cg2 if s.startswith('best')]) #re.search('(?i)best', s)])
    all_cg = np.char.lower(cg2)
    # all_cg = np.append(np.char.lower(cg), np.char.lower(cg2))
    all_cg = filter_tweets(all_cg, ['best of','who','the','\si\s','(?i)i\'m'], exclude=True, _or=True)
    all_cg = [a for a in np.unique([b.rstrip() for b in all_cg]) if len(a.split())>2]
    # all_cg = np.array([re.sub("[^a-zA-Z\s]+", "", s) for s in all_cg])
    all_cg = np.array(list(map(lambda s: award_process(s), all_cg)))
    # print(all_cg)
    # print(len(all_cg))
    # test = remove_if_subset(all_cg)
    test = all_cg
    test = np.array(list(map(lambda s: award_process(s), test)))
    fuzzy_dict = fuzzyRatio(test, 90)
    print(fuzzy_dict)
    ret = np.array([k for k,v in fuzzy_dict.items() if v>5])
    ret = remove_if_subset(ret)
    print(np.unique(ret))
    print(len(np.unique(ret)))
    # print(len([a for a in np.unique([b.rstrip() for b in all_cg]) if len(a.split())>2]))

def get_awards(year):
    tweets = load_tweets(f'../data/gg{year}.json')
    # award_tweets = filter_tweets(tweets, ["(award\s|nominated\s|nomination\s|goes to\s|winner|won|wins|winning|\shttp)"])
    award_tweets = filter_tweets(tweets, ['(?i)rt\s','[Dd](ress|ressed)','(?i)(ever|worst|moment|moments|insults|jokes|insult|joke|http|best use|presenter|host)'], exclude=True, _or=True)
    cg = capture_groups(award_tweets, "(?i)(best\s(.*?))(?:\sgoes to|\sto|\swinner|[.!?$])")
    cg = np.array([s for s in cg if re.search('(?i)best', s) and not re.search('[#@]', s)])
    cg2 = capture_groups(award_tweets, "(?i)(?:wins\s|winner of\s)(?:(best\s(.*?))(?=\shttp|\sto|\sand|\sat|\sfor|\swinner|\sis|[.!?$|#@]))")
    cg2 = np.array([s for s in cg2 if re.search('(?i)best', s) and not re.search('[#@]', s)])
    # cg3 = capture_groups(award_tweets, "(?i)(?:wins\s)(?:(best\s(.*?))(?=\sat|\sfor|\swinner|\sis|[.!?$]))")
    # cg3 = np.array([s for s in cg3 if re.search('(?i)best', s)])
    # print(cg)
    # print(len(cg))
    # print(cg2)
    # print(len(cg2))
    # print(len(cg3))
    # print(cg3)
    all_cg = np.append(np.char.lower(cg), np.char.lower(cg2))
    all_cg = np.array([s for s in all_cg if len(s.split()) >= 3])
    all_cg = np.array([s for s in all_cg if s.startswith('best')])
    all_cg = filter_tweets(all_cg, ['best of'], exclude=True)
    print(all_cg)
    print(len(all_cg))
    # processed = award_process(all_cg)
    # processed = np.array(list(map(lambda s: award_process(s), all_cg)))
    # remove_processed = np.array([s for s in processed if not re.search('(?i)(golden globes|goldenglobes|\sfor\s[a-s]|#|http)', s)])
    # fuzzy_dict = fuzzyRatio(remove_processed, 90)
    # print(fuzzy_dict)
    # ret = np.array([k for k,v in fuzzy_dict.items() if v>10])
    # return ret


def remove_if_subset(strs):
    return [s for s in strs if not any( all(sub in s2 for sub in re.sub("[^\w]+", '', s).split()) for s2 in strs if s!=s2)]

def award_process(award):
    award = re.sub('best actor','best performance by an actor', award) #award.replace('best actor','best performance by an actor')
    award = re.sub('best actress','best performance by an actress', award)
    award = re.sub('supporting actor', 'performance by an actor in a supporting role', award)
    award = re.sub('supporting actress', 'performance by an actress in a supporting role', award)
    award = re.sub('(?i)tv', 'television', award)
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
                    else: d[other] +=1
                else:
                    if len(c)>len(other):
                        d[c] += 1
                    else: d[other] +=1
    return d

get_nominees('2013')
# res = get_awards2("2015")
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