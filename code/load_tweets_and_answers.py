import json
import numpy as np


def load_tweets(filename):
    ''' 
        Returns text of all tweets in a numpy array 
    '''
    with open(filename) as f:
        data = json.load(f)
    return np.array([tweet.get('text') for tweet in data])


def load_answers(filename):
    ''' 
        Returns list of hosts, awards, nominees, presenters, and winners 
        that our code will be checked against.
    '''

    with open(filename) as f: data = json.load(f)
    hosts = data['hosts']
    award_data = data['award_data']
    awards = list(award_data.keys())
    rest = [{k: award_data[k][key] for k in awards} for key in ['nominees','presenters','winner']]
    nominees, presenters, winner = rest[0], rest[1], rest[2]
    return {"hosts": hosts, "awards": awards, "nominess": nominees, "presenters": presenters, "winner": winner}

# hosts, awards, nominees, presenters, winner = load_answers('gg2013answers.json')
# tweets = load_tweets('gg2013.json')