import json
from collections import defaultdict
from flask import Flask, request, Response
from pytrie import Trie
import uuid
import requests
import time
import re

app = Flask(__name__)

data = list()
country_index = defaultdict(list)
name_index = dict()
domain_index = defaultdict(list)

# Time to wait before allowing an update to our dataset. 86400 seconds = 24 hours
UPDATE_WAIT_TIME = 86400


@app.route("/search")
def search():
    if not data_loaded:
        load_data()

    country = request.args.get('country')
    name = request.args.get('name')
    domain = request.args.get("domain")
    filtered = data

    if name and country:
        country = country.lower()
        regex = re.compile(r'\b{0}'.format(name.lower()))
        name_filtered = [uni for uni in data if regex.search(uni['name'].lower())]
        filtered = [uni for uni in name_filtered if uni['country'].lower() == country]

    elif name:
        regex = re.compile(r'\b{0}'.format(name.lower()))
        filtered = [uni for uni in data if regex.search(uni['name'].lower())]
    elif country:
        country = country.lower()
        filtered = country_index[country]
    elif domain:
        filtered = domain_index[domain]

    return Response(json.dumps(filtered), mimetype='application/json')

data_loaded = False
last_updated = 0


def load_data():
    global data_loaded, data
    response = requests.get("https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json")
    data = response.json()
    data_loaded = True

@app.route('/update')
def update():
    global last_updated

    if (time.time() >= last_updated + UPDATE_WAIT_TIME):
        load_data()
        last_updated = time.time()
        response = {'status': 'success', 'message': 'Dataset updated!'}
    else:
        response = {'status': 'error', 'message': 'Dataset had been updated recently. Try again later.'}

    return json.dumps(response)

@app.route('/')
def index():

    if not data_loaded:
        load_data()

    data = {'author': {'name': 'hipo', 'website': 'http://hipolabs.com'},
            'example': 'http://universities.hipolabs.com/search?name=middle&country=Turkey',
            'github': 'https://github.com/Hipo/university-domains-list'}
    return json.dumps(data)

if __name__ == "__main__":
    app.run(debug=False)
