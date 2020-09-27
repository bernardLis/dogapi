import os
import re
import json
import requests
import sys
import redis
import random

from pprint import pprint
from random import choice
from cs50 import SQL
from datetime import date, datetime, timedelta
from flask import Flask, flash, jsonify, redirect, render_template, request, session, request, url_for, send_file, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from flask_wtf.csrf import CSRFProtect

# Configure application
app = Flask(__name__)
application = app # our hosting requires application in passenger_wsgi

# https://flask-wtf.readthedocs.io/en/stable/csrf.html?fbclid=IwAR25LkK-Hw3ii8UuL-tD-GVVVYcve8XqMNV8VM1TB0Gh-JxQcBVcpSmH2BU
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    csrf.init_app(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make session data persistent
# https://pythonise.com/series/learning-flask/flask-session-object
# TEMP secret key for sessions
app.config["SECRET_KEY"] = "APACHE"
app.config.from_object(__name__)

app.config["DOG_IMGS"] = "static/dogs"

# Configure session to use redis (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dogs.db")

# base url
BASE_URL = "https://api.doggo.fans/"
Session(app)

# renders all useful links
@app.route("/", methods=["GET"])
def index():
    """Doggo App"""
    pathToDogs = os.path.join(app.root_path + "/static/dogs")

    links = []
    randomDog = BASE_URL + 'randomDog/' + "13"
    links.append(randomDog)
    for root, dirs, files in os.walk(pathToDogs):
        for dir in dirs:
            dirStr = re.split(r'[-_]', dir)
            breed = ""
            for i, str in enumerate(dirStr):
                if i == (len(dirStr) - 1):
                    breed = breed + dirStr[i].capitalize()
                elif i != 0:
                    breed = breed + dirStr[i].capitalize() + "_"
            url = BASE_URL + 'breed/' + breed
            links.append(url)

    return render_template('index.html', pathToDogs=pathToDogs, links=links)

# returns links to a number of random doggos
@app.route("/randomDog/<n>", methods=["GET"])
def randomDog(n):
    dogs = []
    for i in range(int(n)):
        # get a random dog from db
        rng = random.randint(1, 20580)
        randomDog = db.execute("SELECT * FROM dogs LIMIT 1 OFFSET ?", rng)

        # format the url
        line = randomDog[0]["path"].replace("\\", "/")
        URL = BASE_URL + "img" + line

        # add it to the list
        dogs.append(URL)

    return jsonify(dogs)

# Returns a random picture of a breed passed in the argument
@app.route("/breed/<s>", methods=["GET"])
def breed(s):
    pathToDogs = os.path.join(app.root_path + "/static/dogs")

    correctFolder = ""
    for root, dirs, files in os.walk(pathToDogs):
        for dir in dirs:
            dirStr = re.split(r'[-_]', dir)
            breed = ""
            for i, str in enumerate(dirStr):
                if i == (len(dirStr) - 1):
                    breed = breed + dirStr[i].capitalize()
                elif i != 0:
                    breed = breed + dirStr[i].capitalize() + "_"
            if breed == s:
                correctFolder = dir

    randomFile = random.choice(os.listdir(pathToDogs+'/'+correctFolder))
    pathToFile = correctFolder+'/'+randomFile

    url = BASE_URL + "img/" + pathToFile

    return redirect(url)

# returns a page with a random doggo img
# different img on refresh
@app.route("/breed/view/<s>", methods=["GET"])
def breedView(s):
    pathToDogs = os.path.join(app.root_path + "/static/dogs")

    correctFolder = ""
    for root, dirs, files in os.walk(pathToDogs):
        for dir in dirs:
            dirStr = re.split(r'[-_]', dir)
            breed = ""
            for i, str in enumerate(dirStr):
                if i == (len(dirStr) - 1):
                    breed = breed + dirStr[i].capitalize()
                elif i != 0:
                    breed = breed + dirStr[i].capitalize() + "_"
            if breed == s:
                correctFolder = dir

    randomFile = random.choice(os.listdir(pathToDogs+'/'+correctFolder))
    pathToFile = correctFolder+'/'+randomFile

    url = BASE_URL + "img/" + pathToFile

    return render_template('breedView.html', img=url)

@app.route("/img/<path:path>", methods=["GET"])
def displayDog(path):
    return send_from_directory('static/dogs/', filename=path)
