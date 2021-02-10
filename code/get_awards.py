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
    # 2015: 1754153 
    # 2013: 0174643
    print(f'There are {len(tweets)} total tweets.')
    award_tweets = filter_tweets(tweets, ['(?i)rt\s','[Dd](ress|ressed)','(?i)(ever|worst|moment|moments|insults|jokes|insult|joke|presenter|recovery|pick|soundtrack|achievement|deserving|sex|picture)'], exclude=True, _or=True)
    award_tweets = filter_tweets(award_tweets, ['(?i)best'])
    cg2 = capture_groups(award_tweets, "(?i)(?:wins\s|won\s|nominated for\s|nominees for\s|nominations for\s)(?:(best\s(.*?))(?=\shttp|\sto|\sand|\sat|(?!\smade)\sfor|\swinner|\sis|\sat|[.!?$:|#@]|\swell|\swith|\s\"|\sgolden|\sglobe|\s\(|\s[0-9+]|\sand|\saward|\slol|\sright|\sare|\son|\sbut|,but|\sover|\sgo|\slast|\scamp\s|\smy|\swas|\sis|\sas|\sfirst|\sthat|\sof))")
    cg2 = np.array([s for s in cg2 if s.startswith('best')]) #re.search('(?i)best', s)])
    all_cg = np.char.lower(cg2)
    all_cg = filter_tweets(all_cg, ['best of','who','the','\si\s','(?i)i\'m','after','camp','was','earlier','is','best picture','creator','mentioned','school','pick'], exclude=True, _or=True)
    all_cg = [a for a in np.unique([b.rstrip() for b in all_cg]) if len(a.split())>1]
    test = all_cg
    test = np.array(list(map(lambda s: award_process(s), test)))
    fuzzy_dict = fuzzyRatio(test, 90, lessThan=False)
    print({k: v for k, v in sorted(fuzzy_dict.items(), key=lambda item: item[1])})
    if (len(fuzzy_dict.keys()) > 150):
        ret = np.array([k for k,v in fuzzy_dict.items() if v>(round(max(fuzzy_dict.values()))*0.2)])
    else: 
        ret = np.array([k for k,v in fuzzy_dict.items()])
    print(f'ret is {len(ret)} / {len(fuzzy_dict.keys())} in dict')
    ret = spell_checker(ret)
    ret = filter_tweets(ret, ['(?i)(season|that|so|featured|were|pick|school|both|categories|definitely)'], exclude=True, _or=True)
    ret = split_take_first(ret, ' camp')
    ret = remove_after_word(ret, '(?i)^(.*?)(drama|musical)')
    ret = remove_if_subset(ret)
    print(f'len before add: {len(ret)}')
    ret = add_awards(ret)
    ret = remove_if_subset(ret)
    ret = remove_if_all_in(ret)
    ret = np.array(list(map(lambda s: award_process(s), ret)))
    # ret = spell_checker(ret)
    print(f'len after add: {len(ret)}')
    unique = np.unique(ret)
    print(unique)
    print(len(unique))

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
    # return [s for s in strs if not any( all(sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s2) or sub=='or' for sub in multi_sub([["[\/.,-]", ' '],["[^\w\s]+", '']], s)) for s2 in strs if s!=s2)]

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

# TODO: replace 'show' with 'series' 
#       replace 'movie' with 'motion picture'
#       just 'series' -> 'television series'
#       just 'television' -> 'television series'
def award_process(award):
    award = re.sub('best actor','best performance by an actor', award) #award.replace('best actor','best performance by an actor')
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

res = get_awards("2013")
# t = ['best director camp performance', 'best animated feature']
# print(split_take_first(t, ' camp'))
# t = ['best performance by an actress drama i she', 'best television series comedy featured major trans characters']
# print(remove_after_word(t, '(?i)^(.*?)(drama|comedy)'))
# d = {'best acceptance speech': 2, 'best accessory': 2, 'best acror': 2, 'best act': 2, 'best actrees in a television series serie or': 2, 'best animated': 2, 
# 'best animated feature': 2, 'best animated feature again': 2, 'best animated feature again just happen': 2, 'best animated feature film': 2, 
# 'best animated feature, excuse me while i': 2, 'best animated film': 2, 'best animated film, which': 2, 'best animated motion picture': 2, 
# 'best animated picture': 2, 'best animated won best animation': 2, 'best animation': 2, 'best animation film': 2, 'best antagonist of human history': 2, 
# 'best appetizers': 2, 'best beard of': 2, 'best bestie, best sweatpants': 2, 'best button lady': 2, 'best cleavage': 2, 'best comedian': 2, 'best comedy': 2, 
# 'best comedy actor': 2, 'best comedy actress': 2, 'best comedy film': 2, 'best comedy motion picture': 2, 
# "best comedy motion picture, it still shouldn't have won": 2, 'best comedy motion picture/best original screenplay': 2, 'best comedy musical actress': 2, 
# 'best comedy o wait wtf': 2, 'best comedy of': 2, 'best comedy or musical': 2, 'best comedy or musical - so deserved': 2, 'best comedy or musical film': 2, 
# 'best comedy or was that not announced yet': 2, 'best comedy seriess that how we watch television': 2, 
# 'best comedy television series last year, gets even better in year': 2, 
# 'best comedy, television series creator mentioned leelah alcorn in her acceptance speech': 2, 'best comedy/musical': 2, 
# 'best comedy/musical actor': 2, 'best comedy/musical film': 2, 'best comedy/musical motion picture': 2, 'best comedy/musical somehow': 2, 
# 'best comedy/musical television series': 2, 'best director': 2, 'best director &amp; patricia won performance by an actress in a supporting role': 2, 
# 'best director an best picture': 2, 'best director boyhood': 2, 'best director comedy or musical': 2, 'best director in a motion picture drama,': 2, 
# 'best director of a motion picture': 2, 'best director yasssss 🙌👏👏👏👏': 2, 'best director, beating grand budapest hotel': 2, 'best drama': 2, 
# 'best drama actor': 2, "best drama actor so we'll play off eddie redmayne super fast": 2, 'best drama actress': 2, 'best drama film': 2, 
# 'best drama picture': 2, 'best drama, still think it should have been imitation game': 2, 'best dramatic actor,': 2, 'best drunk speech': 2, 
# 'best dynamic duo': 2, 'best eclectic suit': 2, 'best female actor in supporting role': 2, 'best female actress in drama television series': 2, 
# 'best female comedy role': 2, 'best fi': 2, 'best film': 2, 'best film - musical or comedy': 2, 'best film ant best director': 2, 
# 'best film comedy': 2, 'best film dra': 2, 'best film of': 2, 'best film-musical/comedy': 2, 'best for': 2, 'best foreign': 2, 
# 'best foreign film, just in time': 2, 'best foreign lan': 2, 'best foreign language film': 2, 'best foreign language film come from': 2, 
# 'best foreigner motion picture': 2, 'best fry cook in a supporting role': 2, 'best hair': 2, 'best hat': 2, 'best hat in a television series': 2, "best host of 'quick slants'": 2, 
# 'best impersonation of a child molester': 2, 'best jackie kennedy red carpet impersonation': 2, 'best jewelry': 2, 'best lead actress': 2, 'best lead actress in a motion picture, comedy or musical': 2, 'best lead pizza eaters': 2, 'best leading, support, director, screenwriter': 2, 
# 'best look': 2, 'best looking': 2, 'best lyrics': 2, 'best male performance': 2, 'best mini television series category': 2, 'best mini television series filmed in calgary': 2, 'best mini-series television series': 2, 'best mini-series television series actress': 2, 'best mini-series television series cue dramatic music': 2, 'best mini-series/television motion picture': 2, 'best mini-television series or motion picture made': 2, 'best motion picture - musical/comedy': 2, 'best motion picture already when it just': 2, 'best motion picture before television series did': 2, 'best motion picture comedy': 2, 'best motion picture comedy/musical': 2, 'best motion picture drama, director': 2, 'best motion picture drama; linklater won best director &amp; more': 2, 'best motion picture last yr': 2, 'best motion picture, director &amp; performance by an actress in a supporting role': 2, 'best motion picture, musical or comedy': 2, 'best motion picture-drama after earlier results': 2, 'best motion picture; richard linklater': 2, 'best musical or comedy': 2, 'best musical or comedy film': 2, 'best musical/comedy': 2, 'best musical/comedy film': 2, 'best musical/comedy film actress': 2, 'best narrator': 2, 'best new artist': 2, 'best one': 2, 'best orginal screenplay': 2, 'best orig song': 2, 'best original in a motion picture': 2, 'best original score': 2, 'best original score, hans zimmer': 2, 'best original song': 2, 'best original song were seated closer than some nominees': 2, 'best original song “glory” in a film': 2, 'best outfit': 2, 'best passive aggressive acceptance speech': 2, 'best performance as a mobile spectator': 2, 'best performance by an actor': 2, 'best performance by an actor comedy/musical': 2, "best performance by an actor from next year's": 2, 'best performance by an actor in a comedy as a grandpa': 2, 'best performance by an actor in a comedy/musical motion picture': 2, 'best performance by an actor in a drama was so stacked, dear': 2, 'best performance by an actor in a motion picture, comedy/musical': 2, 'best performance by an actor in a supporting role': 2, 'best performance by an actor in a supporting role glad he won': 2, 'best performance by an actor in a supporting role in a drama': 2, 'best performance by an actor in a supporting role in a mini-series or television motion picture': 2, 'best performance by an actor in a supporting role in whiplash': 2, 'best performance by an actor in a supporting role, no surprise': 2, 'best performance by an actor in a television motion picture or mini-series': 2, 'best performance by an actor in a television series motion picture': 2, 'best performance by an actor in big eyes': 2, 'best performance by an actor in birdman, great performance': 2, 'best performance by an actor in motion picture': 2, 'best performance by an actor in television comedy/musical series': 2, 'best performance by an actor in television series - drama house of cards': 2, "best performance by an actor in this year's": 2, 'best performance by an actor just started my day off': 2, 'best performance by an actor television series': 2, 'best performance by an actor, motion picture comedy or musical': 2, "best performance by an actress even though she's": 2, 'best performance by an actress in a motion picture television series or musical': 2, 'best performance by an actress in a motion picture, musical or comedy,': 2, 'best performance by an actress in a supporting role in a comedic role': 2, 'best performance by an actress in a supporting role in a mini-television series or motion picture': 2, 'best performance by an actress in a supporting role in best performance by an actress in a supporting role in a mini-television series': 2, 'best performance by an actress in a supporting role in this living room if nowhere else': 2, "best performance by an actress in a supporting role, first of hopefully much 'boyhood' love": 2, 'best performance by an actress in a supporting role, motion picture': 2, 'best performance by an actress in a television series or mini-series': 2, 'best performance by an actress in tears': 2, 'best performance by an actress mini-series, television motion picture': 2, 'best performance by an actress television motion picture/mini-series': 2, 'best performance by an actress, comedy in veep,': 2, 'best performance by an actress,love her': 2, 'best performance by an actress-- drama -- she': 2, 'best performance by an actress/television mini-series': 2, 'best performance of a choking qb': 2, 'best pic': 2, 'best picture': 2, 'best picture - musical/comedy': 2, 'best picture besides selma': 2, 'best picture comedy': 2, 'best picture comedy, beats birdman': 2, 'best picture comedy/musical': 2, 'best picture guys': 2, 'best picture it might as': 2, 'best picture musical or comedy': 2, 'best picture of': 2, 'best podcast': 2, 'best podcast about an old loser': 2, 'best rap artist': 2, 'best rebirth streamer': 2, 'best rick': 2, 'best score': 2, 'best score or song': 2, 'best screenplay': 2, 'best screenplay fuckyes': 2, 'best screenplay, birdman': 2, 'best screenplay, hope that': 2, 'best screenplay, it was brill': 2, 'best screenplay, motion picture': 2, 'best screenplay, no contest': 2, 'best script': 2, 'best smile': 2, 'best song': 2, 'best song again': 2, 'best song from a guy in an afro': 2, 'best song from a motion picture': 2, 'best song in motion picture': 2, 'best song were written by pop stars': 2, 'best speech': 2, 'best supportin action in a motion picture': 2, 'best supporting': 2, 'best supporting accessory': 2, 'best supporting creep': 2, 'best supporting facial hair': 2, 'best supporting film actor': 2, 'best supporting television series actor': 2, 'best supportive actress in a television series': 2, 'best suppprting actress': 2, 'best t': 2, 'best television mini-series or motion picture': 2, 'best television series -- someone f----ed someone': 2, 'best television series actor': 2, 'best television series actor in a drama': 2, 'best television series comedy featured major trans characters': 2, 'best television series comedy were about ladies, tech nerds,': 2, 'best television series dram': 2, 'best television series drama actor': 2, 'best television series drama actress in my book': 2, 'best television series drama, first season': 2, 'best television series musical or comedy': 2, 'best television series performance by an actor in a supporting role': 2, 'best television series, here it': 2, 'best telivision ser': 2, 'best tux': 2, 'best tuxedo': 2, 'best vine': 2, 'best “actress”': 2, 'bestie, best sweatpants': 2, 'best comedy television series': 3, 'best drama motion picture': 3, 'best drama television series': 3, 'best foreign film': 3, 'best foreing film': 3, 'best motion picture': 3, 'best motion picture-comedy or musical': 3, 'best performance by an actor comedy': 3, 'best performance by an actor drama': 3, 'best performance by an actor in a supporting role in a television series': 3, 'best performance by an actor-drama': 3, 'best performance by an actor/comedy': 3, 'best performance by an actress in a supporting role – firstpost': 3, 'best picture drama': 3, 'best picture- comedy or musical': 3, 'best picture-drama': 3, 'best television drama series': 3, 'best television mini-series': 3, 'best television motion picture mini-series': 3, 'best television motion picture/mini-series': 3, 'best television series comedy': 3, 'best television series comedy/musical': 3, 'best television series,comedy': 3, 'best television/mini series': 3, 'best animated feature-': 4, 'best animated films': 4, 'best animated motion picture of': 4, 'best animation 🐉': 4, 'best best motion picture drama; linklater won best director &amp; more': 4, 'best comedy in a motion picture': 4, 'best comedy television series deal': 4, 'best comedy,': 4, 'best director,': 4, 'best dramatic motion picture': 4, 'best dramatic picture': 4, 'best dramatic television series': 4, 'best female performance': 4, 'best film drama': 4, 'best film drama,': 4, 'best foreign…': 4, 'best in television series': 4, 'best lead actress in a motion picture, comedy or musical,': 4, 'best mini-series / television motion picture': 4, 'best motion picture comedy/musical,': 4, 'best motion picture drama': 4, 'best motion picture-drama': 4, 'best original screenplay': 4, 'best original song in a motion picture': 4, 'best performance by an actor comedy or musical': 4, 'best performance by an actor in a musical or comedy': 4, 'best performance by an actor in a supporting role,': 4, 'best performance by an actor in a television series comedy/musical': 4, 'best performance by an actor in a television series, musical or comedy': 4, 'best performance by an actor in mini-series television series': 4, 'best performance by an actor in musical or comedy': 4, 'best performance by an actor in television comedy/musical series,': 4, 'best performance by an actor in television mini-series or motion picture': 4, 'best performance by an actor in television series': 4, 'best performance by an actor in television series comedy or musical': 4, 'best performance by an actor motion picture drama': 4, 'best performance by an actor**': 4, 'best performance by an actor,  finally': 4, 'best performance by an actor, comedy/musical film': 4, 'best performance by an actor, finally': 4, 'best performance by an actress': 4, 'best performance by an actress comedy/musical': 4, 'best performance by an actress in a comedy': 4, 'best performance by an actress in a drama film': 4, 'best performance by an actress in a dramatic motion picture': 4, 'best performance by an actress in a film, drama,': 4, 'best performance by an actress in a musical or comedy television series': 4, 'best performance by an actress in a supporting role in a television series mini series or motion picture': 4, 'best performance by an actress in a supporting role in television series': 4, 'best performance by an actress in a television comedy series': 4, 'best performance by an actress in a television comedy series or musical': 4, 'best performance by an actress television series comedy': 4, 'best performance by an actress, musical or comedy': 4, 'best picture,': 4, 'best picture, comedy, musical': 4, 'best picture, musical of comedy': 4, 'best score,': 4, 'best screenplay,': 4, 'best song in a motion picture': 4, 'best song,': 4, 'best television series actress': 4, 'best television series comedy/ musical': 4, 'best television series performance by an actress in a supporting role': 4, 'best  television series musical or comedy': 5, 'best mini television series': 5, 'best mini-television series': 5, 'best motion picture, musical or comedy,': 5, 'best performance by an actor in a mini-series/television motion picture': 5, 'best performance by an actor in a supporting role in a motion picture': 5, 'best performance by an actor, motion picture comedy or musical,': 5, 'best performance by an actress in a supporting role - firstpost': 5, 'best performance by an actress in a supporting role in a series, mini series or television motion picture': 5, 'best performance by an actress in a supporting role in a series, mini-series or television motion picture': 5, 'best performance by an actress in motion picture': 5, 'best performance by an actress in television mini-series or motion picture': 5, 'best performance by an actress motion picture comedy or musical': 5, 'best performance by an actress--television series drama': 5, 'best picture, comedy or musical': 5, 'best screen play, motion picture': 5, 'best screenplay - motion picture': 5, 'best television series, musical or comedy': 5, 'best animated feature ,': 6, 'best foreign film*': 6, 'best mini series or television motion picture now': 6, 'best motion picture - comedy/musical': 6, 'best performance by an actor in a comedy/musical': 6, 'best performance by an actor in best drama': 6, 'best performance by an actor in mini-series or television motion picture': 6, 'best performance by an actor television series comedy': 6, 'best performance by an actor television series drama': 6, 'best performance by an actor, drama': 6, 'best performance by an actress in a comedy motion picture': 6, 'best performance by an actress in a comedy or musical motion picture': 6, 'best performance by an actress in a motion picture comedy/musical': 6, 'best performance by an actress in a supporting role': 6, 'best performance by an actress in a supporting role in a television series, mini-series or motion picture': 6, 'best performance by an actress in a television motion picture or mini-series': 6, 'best performance by an actress in musical, comedy': 6, 'best performance by an actress,': 6, 'best picture, drama': 6, 'best picture, drama,': 6, 'best screenplay of a motion picture': 6, 'best television motion picture mini-series actor': 6, 'best television series': 6, 'best television series actress,': 6, 'best television series comedy or musical': 6, 'best television series comedy,': 6, 'best television series drama actress': 6, 'best mini-series or television motion picture': 7, 'best motion picture - musical or comedy': 7, 'best motion picture, drama': 7, 'best motion picture- drama': 7, 'best performance by an actor in': 7, 'best performance by an actor in a comedy': 7, 'best performance by an actor in a motion picture': 7, 'best performance by an actor in a television mini-series or motion picture': 7, 'best performance by an actor in a television series': 7, 'best performance by an actor in television series, comedy or musical': 7, 'best performance by an actor 👏👍': 7, 'best performance by an actress  television series comedy': 7, 'best performance by an actress in a supporting role in a motion picture': 7, 'best television series dramz': 7, 'best television series,drama': 7, 'best television series-drama': 7, 'best mini-series or television motion picture in': 8, 'best motion picture comedy or musical': 8, 'best performance by an actor in a comedy/musical television series': 8, 'best performance by an actor in a motion picture drama': 8, 'best performance by an actor in a series, mini or television motion picture': 8, 'best performance by an actor in comedy or musical': 8, 'best performance by an actor in television drama series': 8, 'best performance by an actress in a comedy/musical': 8, 'best performance by an actress in a comedy/musical television series': 8, 'best performance by an actress in a mini-series/television motion picture': 8, 'best performance by an actress in a mini-television series': 8, 'best performance by an actress in a motion picture': 8, 'best performance by an actress in a supporting role -': 8, 'best performance by an actress in a supporting role in a television series': 8, 'best performance by an actress in a supporting role in a television series or mini-series': 8, 'best performance by an actress in a supporting role in gg': 8, 'best performance by an actress in a supporting role in television mini series': 8, 'best picture - drama': 8, 'best picture in comedy or musical': 8, 'best picture, comedy or musical,': 8, 'best television series - comedy': 8, 'best television series, comedy or musical': 8, 'best performance by an actor - drama': 9, 'best performance by an actor in a mini series or television motion picture': 9, 'best performance by an actor in a mini-series television series': 9, 'best performance by an actress - television series drama': 9, 'best performance by an actress in a television series': 9, 'best performance by an actress in mini-series television series': 9, 'best motion picture - drama': 10, 'best motion picture, comedy or musical': 10, 'best performance by an actor in a comedy or musical': 10, 'best performance by an actor in a motion picture, drama': 10, 'best performance by an actor in a television  mini-series or motion picture': 10, 'best performance by an actor in mini television series': 10, 'best performance by an actress in a mini-series television series': 10, 'best performance by an actress in a musical or comedy': 10, 'best performance by an actress in a supporting role in a television series drama': 10, 'best performance by an actress, drama': 10, 'best performance by an actress, drama,': 10, 'best television series - comedy or musical': 10, 'best television series drama': 10, 'best performance by an actor in a drama': 11, 'best performance by an actor in a motion picture - drama': 11, 'best performance by an actor in television series drama': 11, 'best performance by an actress drama': 11, 'best motion picture -comedy or musical': 12, 'best motion picture- comedy or musical': 12, 'best performance by an actor in a comedy television series': 12, 'best performance by an actor in a comedy television series,': 12, 'best performance by an actor in a mini-series or television motion picture': 12, 'best performance by an actor in a motion picture comedy or musical': 12, 'best performance by an actor in a supporting role in a television series, mini-series or television motion picture': 12, 'best performance by an actor in a television mini-series': 12, 'best performance by an actor in a television series comedy or musical': 12, 'best performance by an actor in drama': 12, 'best performance by an actor in drama television series': 12, 'best performance by an actress in a comedy or musical': 12, 'best performance by an actress in a comedy television series': 12, 'best performance by an actress in a drama': 12, 'best performance by an actress in a drama television series': 12, 'best performance by an actress in a supporting role in a television series, mini series or television motion picture': 12, 'best performance by an actress in television series comedy': 12, 'best motion picture in comedy or musical': 13, 'best performance by an actor in best television mini-series or motion picture': 13, 'best performance by an actress in a television mini-series or motion picture,': 13, 'best performance by an actress in a television series comedy/musical': 13, 'best television series drama,': 13, 'best television series, drama': 13, 'best performance by an actor in a drama television series': 14, 'best performance by an actress in a comedic television series': 14, 'best performance by an actress in a mini-series television series/motion picture': 14, 'best performance by an actress in a motion picture drama': 14, 'best performance by an actress in a television series comedy or musical': 14, 'best performance by an actress in motion picture, comedy or musical': 14, 'best motion picture -- comedy or musical': 15, 'best performance by an actress in a mini series or television motion picture': 15, 'best performance by an actor in a motion picture, comedy or musical,': 16, 'best performance by an actress in a mini-series or television motion picture': 16, 'best performance by an actress in a motion picture - comedy or musical': 16, 'best performance by an actor in a television series comedy': 17, 'best performance by an actor in a television series drama': 17, 'best performance by an actor in a television series drama,': 17, 'best performance by an actress in a motion picture, drama': 17, 'best performance by an actress in a motion picture, drama,': 17, 'best performance by an actress in a television series comedy': 17, 'best performance by an actress in television series drama,': 17, 'best performance by an actress, in a motion picture, drama': 17, 'best television series - drama': 17, 'best performance by an actor in a television series, drama': 18, 'best television series, drama,': 18, 'best television series or drama': 20, 'best television series- drama -': 20, 'best performance by an actor in a television series - drama': 21, 'best performance by an actor in a television series - drama,': 21, 'best performance by an actress in a television series, drama': 26, 'best performance by an actress in a television series drama': 27}

# print(round(max(d.values())*0.2))
# test = np.array(['best comedic television series', 'best motion picture i comedy or musical', 'best motion picture in comedy or musical'])
# print(remove_if_all_in(test))

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