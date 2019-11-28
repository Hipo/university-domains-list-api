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
    name_contains = request.args.get('name_contains')
    domain = request.args.get("domain")
    filtered = data

    if name and country:
        name = name.lower()
        country = country.lower()
        name_filtered = prefix_tree.values(prefix=name)
        filtered = [uni for uni in name_filtered if uni['country'].lower() == country]
    elif name_contains and country:
        country = country.lower()
        regex = re.compile(r'\b{0}'.format(name_contains.lower()))
        name_filtered = [uni for uni in data if regex.search(uni['name'].lower())]
        filtered = [uni for uni in name_filtered if uni['country'].lower() == country]
    elif name_contains:
        regex = re.compile(r'\b{0}'.format(name_contains.lower()))
        filtered = [uni for uni in data if regex.search(uni['name'].lower())]
    elif name:
        name = name.lower()
        filtered = prefix_tree.values(prefix=name)
    elif country:
        country = country.lower()
        filtered = country_index[country]
    elif domain:
        filtered = domain_index[domain]

    return Response(json.dumps(filtered), mimetype='application/json')

data_loaded = False
last_updated = 0


def load_data():
    global data_loaded, prefix_tree, data, country_index, name_index, domain_index
    response = requests.get("https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json")
    data = response.json()
    for i in data:
        country_index[i["country"].lower()].append(i)
        name_index[i['name'].lower()] = i
        for domain in i["domains"]:
            domain_index[domain].append(i)
        splitted = i['name'].split(" ")
        if len(splitted) > 1:
            for splitted_name in splitted[1:]:
                name_index[splitted_name.lower() + str(uuid.uuid1())] = i
    prefix_tree = Trie(**name_index)

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
