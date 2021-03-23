from flask import Blueprint, request, current_app, redirect, url_for, render_template
from result import R
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

@controller.route('/search', methods=['GET'])
def search():
    print("Received!")
    # query = request.json.get("query")
    # boolean = request.json.get("boolean")
    # search_desc = request.json.get("search_desc")
    # search_desc = search_desc == 'True'
    imd = request.args
    args_str = str(list(dict(imd).keys())[0])
    args_dict = json.loads(args_str)
    print(args_dict)
    
    query = args_dict["query"]
    boolean = args_dict["boolean"]
    search_desc = args_dict["search_desc"]
    
    # records = service.search(query=query, boolean=boolean, search_desc=search_desc)
    records = service.search_moc(query=query, boolean=["AND", "OR", "OR"], search_desc=True)
    r = R.ok().add_data("list", records)
    r_list = r.data['list']
    # for i in r_list:
    #     print("*"*40)
    #     print(i)
    # return redirect(url_for("app.results",content=r_list))
    print(r_list)
    return render_template("content.html", content=r_list)
    # return jsonify(r)

@controller.route('/results', methods=['GET', 'POST'])
def results():
    return render_template("content.html")
    

@controller.route('/completion/<string:query>', methods=['GET'])
def completion(query):
    # records = service.completion(query)
    records = service.completion_moc(query)
    r = R.ok().add_data("list", records)
    return jsonify(r)


@controller.route('/heatsearch', methods=['GET', 'POST'])
def heat_search():
    return jsonify(service.heat_search_moc())


@controller.route('/', methods=['GET', 'POST'])
@controller.route('/homepage', methods=['GET', 'POST'])
def homepage():
    # r = R.ok().add_data("item", "haha")
    form = SearchForm()
    if form.validate_on_submit():
        print("lalala")
        print(form.query.data)
        print(form.description.data)
        print(form)
        return redirect(url_for('.search',form=form))
    return render_template("homepage.html", form=form)

