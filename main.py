import json

from flask import Flask, render_template
from requests_oauthlib import OAuth2Session
import os

try:
    import secrets # only needed for localhost, that's why it's in the try/except statement
except ImportError as e:
    pass

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/github/login")
def github_login():
    


@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run()