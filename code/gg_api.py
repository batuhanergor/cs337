'''Version 0.35'''
from get_hosts import hosts_get
from get_awards import awards_get
from get_extras import best_dressed, worst_dressed, most_discussed
from workspace import winner_get, presenters_get, finalize_presenters
from Levenshtein import distance as edit_distance
import numpy as np
import time
import os.path
from os import path
import json 

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
tweets = []

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    hosts = hosts_get(year)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards = awards_get(year)
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    actual_awards = OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819
    nominees = {k:['Nathan Timmerman'] for k in actual_awards}
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    actual_awards = OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819
    winners = winner_get(actual_awards, year)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    with open(f'../data/winners{year}.json') as f: 
        winners = json.load(f)
    # winners = winner_get(OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819, year)
    presenters1 = presenters_get(OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819, year)
    presenters = finalize_presenters(winners, presenters1)
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    # get_presenters often returns the winner of the award as the presenter,
    # so get winners for use in finalize_presenters fcn (called in get_presenters), 
    # which takes care of that issue
    for year in ['2013','2015','2018','2019']:
        print(f'\nStarting pre-ceremony processing...')
        if path.exists(f"../data/gg{year}.json") and not path.exists(f"../data/winners{year}.json"):
            winners = get_winner(year)
            with open(f"../data/winners{year}.json", "w") as f:  
                json.dump(winners, f)

    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    while True:
        year = input('Type in a year (2013, 2015, 2018, 2019) to see the results.\nOr type 1 to quit.\n')
        if year == '1': break
        if year not in ['2013','2015','2018','2019']:
            print(f'{year} is not a valid year.\n')
            continue
        if not path.exists(f"../data/gg{year}.json"):
            print(f'File for {year} doesn\'t exist.\n')
            continue
        
        t = time.time()
        print(f'\nCalculating {year} results...')
        print('Getting host...')
        hosts = get_hosts(year)
        print('Getting awards...')
        awards = get_awards(year)
        print('Getting winners...')
        winners = get_winner(year)
        print('Getting presenters...')
        presenters = get_presenters(year)
        # presenters2 = finalize_presenters(winners, presenters1)
        print('Getting nominees...')
        nominees = get_nominees(year)
        print('Getting best dressed...')
        bd = best_dressed(year)
        print('Getting worst dressed...')
        wd = worst_dressed(year)
        print('Getting most discussed...')
        md = most_discussed(year)
        print(f'Time elapsed: {time.time() - t} s')
        print('\n\n')

        # combine:
        actual_awards = OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819
        json = {}
        for award in actual_awards:
            json[award] = {"Presenters": presenters[award], "Nominees": nominees[award], "Winner": winners[award]}

        print(f'Host(s): {", ".join([" ".join(w.capitalize() for w in x.split()) for x in hosts])}\n')
        for k, v in json.items():
            print(f'Award: {" ".join(w.capitalize() for w in k.split())}')
            print(f'Closest scraped award: {" ".join(w.capitalize() for w in awards[np.argmin([edit_distance(k.lower(), a.lower()) for a in awards])].split())}')
            print(f'Presenters: {", ".join([" ".join(w.capitalize() for w in x.split()) for x in v["Presenters"]]) if v["Presenters"] else "Not found"}')
            print(f'Nominees: {", ".join([" ".join(w.capitalize() for w in x.split()) for x in v["Nominees"]]) if v["Nominees"] else "Not found"}')
            print(f'Winner: {" ".join(w.capitalize() for w in v["Winner"].split()) if v["Winner"] else "Not found"}\n')
        
        print(f'Best Dressed: {" ".join(w.capitalize() for w in bd.split())}')
        print(f'Worst Dressed: {" ".join(w.capitalize() for w in wd.split())}')
        print(f'Most Discussed: {" ".join(w.capitalize() for w in md.split())}')

        print(f'\nScraped award names ({len(awards)}):')
        for a in awards:
            print(f'\t- {" ".join(w.capitalize() for w in a.split())}')
        print('\n\n')

    return

if __name__ == '__main__':
    pre_ceremony()
    main()
