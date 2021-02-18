from filter_tweets import filter_tweets, capture_groups, lowercase_array
from load_tweets_and_answers import load_tweets, load_answers
import numpy as np
import pandas as pd
import os
import re
from helper_funcs import levenshtein_dict, get_consecutive_pos, clean
import nltk



# match subsets of terms in input dict and count both towards total
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
            if key2.replace(' ', '').lower() in key.replace(' ', '').lower() and (sorted_dict[key]/total > 0.10 or (sorted_dict[key] > 100 and sorted_dict[key]/total > 0.05)):
                value_to_add += sorted_dict[key2]
                to_remove.append(key2)
            elif key.replace(' ', '').lower() in key2.replace(' ', '').lower():
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

def get_combinations_awards(input):
    new_array = []
    for i in range(len(input) - 1):
        for j in range(1, len(input)):
            if i !=j:
                joined_string = input[i] + " " + input[j]
                new_array.append(joined_string)
    return new_array


def filter_tweets_by_award_type(tweets, award_name):
    if 'best performance by an actress in a mini-series or motion picture made for television' in award_name.lower():
        return tweets
    if 'film' in award_name.lower():
        return_tweets = filter_tweets(tweets, ["Series", "series", "tv", "TV", "Tv"], exclude=True, _or=True)
        return return_tweets
    elif 'motion picture' in award_name.lower():
        return_tweets = filter_tweets(tweets, ["Series", "series", "tv", "TV", "Tv"], exclude=True, _or=True)
        return return_tweets

def groups_around_regex(tweets, regex, position_to_take):
    winners = []
    for tweet in tweets:
        m = re.match(rf"(.*){regex}(.*)", tweet, flags=re.I)
        if m:
            winners.append(m.groups()[position_to_take])
    return(winners)

# add important words not caught be award_pos
def add_key_award_words(award, award_pos):
    if "best" in award:
        award_pos.append('best')
    if "animated" in award:
        award_pos.append('animated')
    if "foreign" in award:
        award_pos.append('foreign')
    if "television series" in award:
        award_pos.append('tv(-series|series)')
    if "mini-series" in award:
        award_pos.append('mini(-series|series)')
    if "motion picture" in award:
        award_pos.append('picture')
        award_pos.append('film')

def extract_award_name(phrase):
    if "director" in phrase:
        return 'best director - motion picture'
    elif "animated" in phrase:
        return 'best animated feature film'
    elif "screenplay" in phrase:
        return 'best screenplay - motion picture'
    elif "foreign" in phrase:
        return 'best foreign language film'
    elif "song" in phrase:
        return "best original song - motion picture"
    elif "score" in phrase:
        return 'best original score - motion picture'
    elif "actor" in phrase:
        if ("supporting" in phrase or "role" in phrase):
            if "picture" in phrase or "movie" in phrase and ("television" not in phrase and "tv" not in phrase and "show" not in phrase):
                return 'best performance by an actor in a supporting role in a motion picture'
            if "picture" in phrase or "movie" in phrase and ("television" in phrase or "tv" in phrase or "show" in phrase):
                return 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television'
            if "mini series" in phrase or "mini-series" in phrase or "miniseries" in phrase or "series" in phrase:
                return 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television'
        if ("supporting" not in phrase and "role" not in phrase):
            if "picture" in phrase or "movie" in phrase:
                if "drama" in phrase:
                    return 'best performance by an actor in a motion picture - drama'
                if "comedy" in phrase or "musical" in phrase:
                    return 'best performance by an actor in a motion picture - comedy or musical'
            if "television" in phrase or "tv" in phrase or "series" in phrase or "show":
                if "drama" in phrase:
                    return 'best performance by an actor in a television series - drama'
                if "comedy" in phrase or "musical" in phrase:
                    return 'best performance by an actor in a television series - comedy or musical'
                if "mini series" in phrase or "mini-series" in phrase or "miniseries" in phrase or "series" in phrase:
                    return 'best performance by an actor in a mini-series or motion picture made for television'
                if "picture" in phrase or "movie" in phrase:
                    return 'best performance by an actor in a mini-series or motion picture made for television'
    elif "actress" in phrase:
        if ("supporting" in phrase or "role" in phrase):
            if "picture" in phrase or "movie" in phrase and ("television" not in phrase and "tv" not in phrase and "show" not in phrase):
                return 'best performance by an actress in a supporting role in a motion picture'
            if "picture" in phrase or "movie" in phrase and ("television" in phrase or "tv" in phrase or "show" in phrase):
                return 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television'
            if "mini series" in phrase or "mini-series" in phrase or "miniseries" in phrase or "series" in phrase:
                return 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television'
        if ("supporting" not in phrase and "role" not in phrase):
            if "picture" in phrase or "movie" in phrase:
                if "drama" in phrase:
                    return 'best performance by an actress in a motion picture - drama'
                if "comedy" in phrase or "musical" in phrase:
                    return 'best performance by an actress in a motion picture - comedy or musical'
                else:
                    return 'best performance by an actress in a motion picture - unknown'
            if "television" in phrase or "tv" in phrase or "series" in phrase or "show" in phrase:
                if "drama" in phrase:
                    return 'best performance by an actress in a television series - drama'
                if "comedy" in phrase or "musical" in phrase:
                    return 'best performance by an actress in a television series - comedy or musical'
                if "mini series" in phrase or "mini-series" in phrase or "miniseries" in phrase or "series" in phrase:
                    return 'best performance by an actress in a mini-series or motion picture made for television'
                if "picture" in phrase or "movie" in phrase:
                    return 'best performance by an actress in a mini-series or motion picture made for television'
                else:
                    return 'best performance by an actress in television - unknown'
    elif "actor" not in phrase and "actress" not in phrase and "role" not in phrase:
        if "television" not in phrase and "tv" not in phrase and "series" not in phrase:
            if "drama" in phrase:
                return 'best motion picture - drama'
            if "comedy" in phrase or "musical" in phrase:
                return 'best motion picture - comedy or musical'
            if "picture" in phrase or "movie" in phrase:
                if "drama" in phrase:
                    return 'best motion picture - drama'
                if "comedy" in phrase or "musical" in phrase:
                    return 'best motion picture - comedy or musical'
        if "television" in phrase or "tv" in phrase or "series" in phrase:
            if "drama" in phrase:
                return 'best television series - drama'
            if "comedy" in phrase or "musical" in phrase:
                return 'best television series - comedy or musical'
            if "picture" in phrase or "movie" in phrase or "mini series" in phrase or "mini-series" in phrase or "miniseries" in phrase or "series" in phrase:
                return 'best mini-series or motion picture made for television'

def filter_by_award(tweets, award):
    return_tweets = []
    if award == 'best animated feature film':
        return_tweets = filter_tweets(tweets, [" best animated", "animated film", "animation"], _or=True)
    if award == 'best foreign language film':
        return_tweets = filter_tweets(tweets, ["foreign"], _or=True)
    if award == 'best original score - motion picture':
        return_tweets = filter_tweets(tweets, ["score"], _or=True)
    if award == 'best original song - motion picture':
        return_tweets = filter_tweets(tweets, ["song"], _or=True)
    if award == 'best director - motion picture':
        return_tweets = filter_tweets(tweets, ["director"], _or=True)
    if award == 'best screenplay - motion picture':
        return_tweets = filter_tweets(tweets, ["screenplay"], _or=True)
    if award == 'best performance by an actress in a supporting role in a motion picture':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actor in a supporting role in a motion picture':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture", "mini series","mini-series", "miniseries", "series"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], _or=True)
    if award == 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture", "mini series", "mini-series", "miniseries", "series"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], _or=True)
    if award == 'best performance by an actor in a motion picture - drama':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actress in a motion picture - drama':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actor in a motion picture - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actress in a motion picture - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show"], exclude=True, _or=True)
    if award == 'best performance by an actor in a television series - drama':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actress in a television series - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actor in a television series - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets,["movie", "picture"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actress in a television series - drama':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actress in a television series - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actor in a mini-series or motion picture made for television':
        return_tweets = filter_tweets(tweets, ["actor"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture", "mini series", "mini-series", "miniseries", "series"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best performance by an actress in a mini-series or motion picture made for television':
        return_tweets = filter_tweets(tweets, ["actress"], _or=False)
        return_tweets = filter_tweets(return_tweets, ["supporting", "role"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture", "mini series", "mini-series", "miniseries", "series"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best motion picture - drama':
        return_tweets = filter_tweets(tweets, ["actor", "actress"], exclude=True ,_or=True)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], exclude=True, _or=True)
    if award == 'best motion picture - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actor", "actress"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], exclude=True, _or=True)
    if award == 'best television series - drama':
        return_tweets = filter_tweets(tweets, ["actor", "actress"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["drama"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], exclude=True, _or=False)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best television series - comedy or musical':
        return_tweets = filter_tweets(tweets, ["actor", "actress"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["comedy", "musical"], _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture"], exclude=True, _or=False)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    if award == 'best mini-series or motion picture made for television':
        return_tweets = filter_tweets(tweets, ["actor", "actress"], exclude=True, _or=True)
        return_tweets = filter_tweets(return_tweets, ["movie", "picture", "mini series", "mini-series", "miniseries", "series"], exclude=True, _or=False)
        return_tweets = filter_tweets(return_tweets, ["television", "tv", "show", "series"], _or=True)
    return return_tweets

def filter_tweets_2_words(tweets, pat1, pat2, exclude=False, _or=False):
    if exclude:
        if _or:
            return tweets[np.vectorize(lambda x: not any([re.search(r, x.lower()) != None for r in pat1]) and
                                                 any([re.search(r, x.lower()) != None for r in pat2]))(tweets)]
        else:
            return tweets[np.vectorize(lambda x: not all([re.search(r, x.lower()) != None for r in pat1]) and
                                                 all([re.search(r, x.lower()) != None for r in pat2]))(tweets)]
    else:
        if _or:
            return tweets[np.vectorize(lambda x: any([re.search(r, x.lower()) != None for r in pat1]) and
                any([re.search(r, x.lower()) != None for r in pat2]))(tweets)]
        else:
            return tweets[np.vectorize(lambda x: all([re.search(r, x.lower()) != None for r in pat1]) and
                all([re.search(r, x.lower()) != None for r in pat2]))(tweets)]


def most_frequent(List):
    counter = 0
    num = List[0]
    for i in List:
        curr_frequency = List.count(i)
        if (curr_frequency > counter):
            counter = curr_frequency
            num = i
    return num

def find_nominees_w_awards(tweets, reg_pat):
    # find potential nominee names without award names
    potential_nominees_phrases_up_for = []
    potential_nominees_phrases_up_for_phrases = []
    for x in tweets:
        #print("tweet: ", tweets)
        if len(re.findall(reg_pat, x)):
            potential_nominees_phrases_up_for.append(re.findall(reg_pat, x))

            for pair in [('best', 1)]:
                potential_nominees_phrases_up_for_phrases = potential_nominees_phrases_up_for_phrases + \
                                                            groups_around_regex(tweets, pair[0], pair[1])
    flat_list = []
    exclude_these = ["golden", "globe", "globes", "best actor", "best actress", "motion picture", "television", "tv",
                     "series"]
    for each_phrase in potential_nominees_phrases_up_for:
        for each_name in each_phrase:
            flat_list.append(each_name.lower())
    result = []
    # find the corresponding award title for each possible nominee
    for i in range(len(flat_list)):
        pot_nom_up_for_tweets = filter_tweets(tweets, [flat_list[i], 'best'], _or=False)
        extracted_award = []
        for each in pot_nom_up_for_tweets:
            extracted_award.append(extract_award_name(each.lower()))
            if most_frequent(extracted_award) is not None and 'best' not in flat_list[i]:
                result.append((flat_list[i], most_frequent(extracted_award)))
    return result


def nominee_get(actual_awards, year):

    tweets = load_tweets(f'../data/gg{year}.json')
    # print(f'Answers: {list(load_answers("../data/gg2013answers.json")["nominees"])}')

    all_best_tweets = filter_tweets(tweets, ["best"], _or=True)
    all_best_tweets = filter_tweets(all_best_tweets,
                                    ["won", "win(s|ning|ner|ners)", "present", "introduced", "(|isn\'t|is not|isn\'t even |is not even) nominated",
                                     "should(\'ve a| have a| \'ve been| have been|) a nom(|inated|ination)",
                                     "should(\'ve got(ten)|have got(ten)|\'ve got(ten) a|have got(ten) a|) nom(inated|ination)",
                                     "did(n\'t get| not get |n\'t get a| not get a) no(m|minated|mination)",
                                     "just won", "(isn\'t| is not| isn\'t a| is not a) no(minated|minee)", "goes to", "congrats", "congratulations"], exclude=True, _or=True)


    # find all potential nominees with "up for"
    up_for_tweets = filter_tweets(all_best_tweets, ["up for best"], _or=True)
    # exclude negations

    nom_result_1 = find_nominees_w_awards(up_for_tweets, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    nom_for_tweets = filter_tweets(tweets, ["nominated for best"], _or=True)
    #print("nom_result_1: ", nom_result_1)
    # exclude negations
    nom_for_tweets = filter_tweets(nom_for_tweets,["not nom(inating|ated)","not a nominee", "n(ot|n\t) get nominated", "not even nom(inating|ated|)", "is(n\'t| not|n\'t even | not even)",
                                                  "is(n\'t nominated| not nominated|n\'t even nominated| not even nominated)",
                                                  "was(n\'t| not)", "was(n\'t even | not even )",
                                                  "was(n\'t nominated| not nominated|n\'t even nominated| not even nominated)",
                                                  "should(\'ve been| have been| be) nominated", "next year"], exclude=True, _or=True)
    nom_result_2 = find_nominees_w_awards(nom_for_tweets, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    #print("nom_result_2: ", nom_result_2)

    should_have_won_tweets = filter_tweets(tweets, ["should(\'ve| have) wo(n|n for) best", "should(\'ve| have) wi(n|n for) best"], _or=True)
    potential_nominees_phrases_should = []
    for pair in [('(.*)(nomin(ee|ees|ated|ation))(.*)for(.*?)', 0), ('(.*)(should have won)(.*)', 0)]:
        potential_nominees_phrases_should = potential_nominees_phrases_should + \
                                     groups_around_regex(should_have_won_tweets, pair[0], pair[1])
    #print("potential_nominees_phrases_should: ", potential_nominees_phrases_should)
    # exclude negations
    should_have_won_tweets = filter_tweets(should_have_won_tweets, ["not nom(inating|ated)","not a nominee", "n(ot|n\t) get nominated", "not even nom(inating|ated|)", "is(n\'t| not|n\'t even | not even)",
                                                  "is(n\'t nominated| not nominated|n\'t even nominated| not even nominated)",
                                                  "was(n\'t| not)", "was(n\'t even | not even )",
                                                  "was(n\'t nominated| not nominated|n\'t even nominated| not even nominated)",
                                                  "should(\'ve been| have been| be) nominated", "next year"], exclude=True, _or=True)
    nom_result_3 = find_nominees_w_awards(should_have_won_tweets, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    should_win_tweets= filter_tweets(tweets, ["should win best", "should win for best"], _or=False)
    nom_result_4 = find_nominees_w_awards(should_win_tweets, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")
    #print("should_win_tweets: ", should_win_tweets)

    nom_tweets1 = filter_tweets(tweets, ["nomin(ee|ees|ated|ation)", "should have won"], _or=True)
    nom_tweets1 = filter_tweets(nom_tweets1, ["best"], _or=True)
    # exclude all tweets with without nominations
    all_nom_tweets = filter_tweets(nom_tweets1,
                                   ["win(s|ning|ner|ners)", "present", "introduced", "(|isn\'t|is not|isn\'t even |is not even) nominated",
                                    "should(\'ve a| have a| \'ve been| have been|) a nom(|inated|ination)",
                                    "should(\'ve got(ten)|have got(ten)|\'ve got(ten) a|have got(ten) a|) nom(inated|ination)",
                                    "did(n\'t get| not get |n\'t get a| not get a) no(m|minated|mination)",
                                    "just won", "(isn\'t| is not| isn\'t a| is not a) no(minated|minee)", "goes to"], exclude=True, _or=True)
    #print("nom_tweets3: ", all_nom_tweets)


    filter_best_actor = filter_tweets(tweets, ["#bestactor", "#bestactress"], _or=True)
    filter_best_actor = filter_tweets(filter_best_actor,
                                   ["won", "win(s|ning|ner|ners)", "present", "introduced", "(|isn\'t|is not|isn\'t even |is not even) nominated",
                                    "should(\'ve a| have a| \'ve been| have been|) a nom(|inated|ination)",
                                    "should(\'ve got(ten)|have got(ten)|\'ve got(ten) a|have got(ten) a|) nom(inated|ination)",
                                    "did(n\'t get| not get |n\'t get a| not get a) no(m|minated|mination)",
                                    "just won", "(isn\'t| is not| isn\'t a| is not a) no(minated|minee)", "goes to", "congrats", "congratulations"], exclude=True, _or=True)
    nom_result_5 = find_nominees_w_awards(filter_best_actor, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    filter_best_actress = filter_tweets(tweets, ["#bestmotion", "#bestmotionpicture", "bestmotionpicture", "#bestpicture", "#musical", "#comedy", "#comedyormusical", "#drama", "#tvseries", "#tvshow", "#series", "#miniseries", "#tv", "#television", "#show"], _or=True)
    filter_best_actress = filter_tweets(filter_best_actress,
                                   ["won", "win(s|ning|ner|ners)", "present", "introduced", "(|isn\'t|is not|isn\'t even |is not even) nominated",
                                    "should(\'ve a| have a| \'ve been| have been|) a nom(|inated|ination)",
                                    "should(\'ve got(ten)|have got(ten)|\'ve got(ten) a|have got(ten) a|) nom(inated|ination)",
                                    "did(n\'t get| not get |n\'t get a| not get a) no(m|minated|mination)",
                                    "just won", "(isn\'t| is not| isn\'t a| is not a) no(minated|minee)", "goes to", "congrats", "congratulations"], exclude=True, _or=True)
    nom_result_6 = find_nominees_w_awards(filter_best_actress, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    filter_best_actress = filter_tweets(tweets, ["#originalscore", "#originalsong", "#screenplay"], _or=True)
    filter_best_actress = filter_tweets(filter_best_actress,
                                   ["won", "win(s|ning|ner|ners)", "present", "introduced", "(|isn\'t|is not|isn\'t even |is not even) nominated",
                                    "should(\'ve a| have a| \'ve been| have been|) a nom(|inated|ination)",
                                    "should(\'ve got(ten)|have got(ten)|\'ve got(ten) a|have got(ten) a|) nom(inated|ination)",
                                    "did(n\'t get| not get |n\'t get a| not get a) no(m|minated|mination)",
                                    "just won", "(isn\'t| is not| isn\'t a| is not a) no(minated|minee)", "goes to", "congrats", "congratulations"], exclude=True, _or=True)
    nom_result_7 = find_nominees_w_awards(filter_best_actress, "([A-Z][\w-]*(?:\s+[A-Z][\w-]*)+)")

    #filtered_out_winners = filter_tweets(filtered_out_winners, ["nom(ination|inee|inated|nominations)", "up for", "should(\'ve| have) won", "should win"], _or=True)

    all_awards_and_nominees = []
    for idx, award in enumerate(actual_awards):
        # print(f'Award {idx + 1} of {len(OFFICIAL_AWARDS_1315)}: {award.title()}')
        # get all possible combinations of award name
        # break down the award name into proper nouns and adjectives
        award_pos = []
        add_key_award_words(award, award_pos)
        award_pos_words = get_consecutive_pos(get_consecutive_pos([award], 'RBS') + [award], 'NN')
        award_pos += award_pos_words

        # exclude cecil b. demille award nominations
        if award == ("cecil b. demille award"):
            all_awards_and_nominees.append({award: []})
        else:

            nominee_results = []
            for each in nom_result_1:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append(each[0])
            for each in nom_result_2:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append(each[0])
            for each in nom_result_3:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append((each[0]))
            for each in nom_result_4:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append((each[0]))
            for each in nom_result_5:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append((each[0]))
            for each in nom_result_6:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append((each[0]))
            for each in nom_result_7:
                if each[1] == award and each[1] not in nominee_results:
                    nominee_results.append((each[0]))

            values, counts = np.unique(nominee_results, return_counts=True)

            # fuzzy match similar terms, giving precedence to the term with a higher count
            match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
            counts_dict, percent_dict = match_subsets(match_fuzzies)

            nominee_results_cleaned = clean(nominee_results, ['golden', 'globe', 'globes' 'golden globes', 'RT', '@',
                                                              'Golden', 'Globe', 'Award', 'Globes', 'Best',
                                                              'supporting', "actor", "actress", "motion", "picture",
                                                              "tv", "television", "series", "show", "foreign", "film",
                                                              "drama"],)

            values, counts = np.unique(nominee_results_cleaned, return_counts=True)

            # fuzzy match similar terms, giving precedence to the term with a higher count
            match_fuzzies = levenshtein_dict(dict(zip(values, counts)), 0.75)
            counts_dict, percent_dict = match_subsets(match_fuzzies)

            # return a dictionary of candidates and counts
            #print(counts_dict)
            #print("counts_dict",counts_dict)
            count_dict_list = list(counts_dict.keys())

            final_nominee_result = []
            if len(count_dict_list) < 5 and len(count_dict_list) > 1:
                for i in range(len(count_dict_list)):
                    final_nominee_result.append(count_dict_list[i])
            if len(count_dict_list) >= 5:
                for i in range(3):
                    final_nominee_result.append(count_dict_list[i])
            all_awards_and_nominees.append({award: final_nominee_result})
            continue
    return(all_awards_and_nominees)


#print(nominee_get(OFFICIAL_AWARDS_1315, 2013))