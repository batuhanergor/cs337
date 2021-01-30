import json
import pandas as pd

def load_tweets(filename):
    return pd.read_json(filename).text.to_numpy()

def load_answers(filename):
    with open(filename) as f:
        data = json.load(f)
    hosts = data["hosts"]
    award_data = data['award_data']
    awards = award_data.keys()
    rest = [{k: award_data[k][key] for k in awards} for key in ['nominees','presenters','winner']]
    nominees, presenters, winner = rest[0], rest[1], rest[2]
    return hosts, awards, nominees, presenters, winner

# hosts, awards, nominees, presenters, winner = load_answers('gg2013answers.json')
# tweets = load_tweets('gg2013.json')