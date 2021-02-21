from flask import Blueprint, request, current_app
from result import R
from utils import *
import service
import time
import pickle

controller = Blueprint('app', __name__)


@controller.route('/search/<string:query>', methods=['GET'])
def search(query):
    # records = service.search(query)
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
    print("start")
    r = R.ok().add_data("item", "haha")

    return jsonify(r)
