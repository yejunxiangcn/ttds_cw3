from flask import Blueprint, request, current_app, redirect, url_for, render_template
from result import R
from utils import *
import service
import json
import time
import pickle
import requests

controller = Blueprint('app', __name__)


@controller.route('/search', methods=['POST'])
def search():
    query = request.json.get("query")
    boolean = request.json.get("boolean")
    search_desc = request.json.get("search_desc")
    search_desc = search_desc == 'True'

    # records = service.search(query=query, boolean=boolean, search_desc=search_desc)
    records = service.search_moc(query=query, boolean=["AND", "OR", "OR"], search_desc=True)
    r = R.ok().add_data("list", records)
    return jsonify(r)


@controller.route('/completion/<string:query>', methods=['GET'])
def completion(query):
    # records = service.completion(query)
    records = service.completion_moc(query)
    r = R.ok().add_data("list", records)
    return jsonify(r)


@controller.route('/heatsearch')
def heat_search():
    return jsonify(service.heat_search_moc())


@controller.route('/')
def homepage():
    # r = R.ok().add_data("item", "haha")
    return render_template("homepage.html")
    # return jsonify(r)

def test():
    url = 'http://127.0.0.1:5000/search'
    d = {'key1': 'value1', 'key2': 'value2'}
    r = requests.post(url, data=d)
