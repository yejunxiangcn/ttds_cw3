from flask import Blueprint, request, current_app, redirect, url_for, render_template
from utils import *
import service
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length
import json
import time
import pickle
import requests

controller = Blueprint('app', __name__)


class SearchForm(FlaskForm):
    query = StringField('query', validators=[InputRequired()])
    description = BooleanField('description')


@controller.route('/searchID/<string:bookID>', methods=['GET'])
def searchID(bookID):
    bookID = str(bookID)
    result = service.searchID(bookID)
    return render_template("content.html", content=result, query=[])


@controller.route('/search', methods=['GET'])
def search():
    imd = request.args
    args_str = str(list(dict(imd).keys())[0])
    args_dict = json.loads(args_str)
    # print(args_dict)

    query = args_dict["query"]
    boolean = args_dict["boolean"]
    search_desc = args_dict["search_desc"] == 'True'
    corrected_query = []

    records = service.search(query=query, boolean=boolean, search_desc=search_desc)
    if len(records) == 0:
        query = [service.correction(q) for q in query]
        records = service.search(query=query, boolean=boolean, search_desc=search_desc)
        corrected_query = query

    if len(records) != 0:
        for q in query:
            service.heat_increase(q)

    print("correction")
    print(corrected_query)

    return render_template("content.html", content=records[:100], query=corrected_query)


@controller.route('/results', methods=['GET', 'POST'])
def results():
    return render_template("content.html")


@controller.route('/completion/<string:query>', methods=['GET'])
def completion(query):
    records = service.completion(query.strip())
    return jsonify(records)


@controller.route('/heatsearch', methods=['GET', 'POST'])
def heat_search():
    return jsonify(service.heat_search())


@controller.route('/', methods=['GET', 'POST'])
@controller.route('/homepage', methods=['GET', 'POST'])
def homepage():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('.search', form=form))
    return render_template("homepage.html", form=form)
