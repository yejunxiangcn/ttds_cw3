from flask import Blueprint, request, current_app
from result import R
from utils import *
import service
import json
import time
import pickle

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


@controller.route('/')
def hello_world():
    r = R.ok().add_data("item", "haha")

    return jsonify(r)
