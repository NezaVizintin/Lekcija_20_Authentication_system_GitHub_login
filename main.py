import json

from flask import Flask, render_template, request, redirect, url_for, make_response
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
    """Step 1: User Authorization.
        Redirect the user/resource owner to the OAuth provider (i.e. Github)
        using an URL with a few key OAuth parameters."""

    # takes GITHUB_CLIENT_ID from secrets.py and with it creates an open authorization (OAuth) session
    # it's an authorization protocol that allows you to approve one application interacting with another on your behalf without giving away your password
    github_oauth_session = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"))

    # you get an authorization url and state from github
    # The state parameter is used by the application to store request-specific data and/or prevent CSRF attacks.
    # The authorization server must return the unmodified state value back to the application.
    authorization_url, state = github_oauth_session.authorization_url("https://github.com/login/oauth/authorize")

    response = make_response(redirect(authorization_url))  # redirects user to GitHub for authorization, authorization url (in this case /github/callback) is set on github when creating your app
    response.set_cookie("oauth_state", state, httponly=True)  # for CSRF purposes, httponly - JS and other scripts can't access the cookie (only the browser and os can)

    return response

    # Step 2: User authorization, this happens on the provider.

@app.route("/github/callback")
def github_callback():
    """ Step 3: Retrieving an access token.
        The user has been redirected back from the provider to your registered
        callback URL. With this redirection comes an authorization code included
        in the redirect URL. We will use that to obtain an access token."""

    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"), state=request.cookies.get("oauth_state")) # creates oauth session same as above but with state parameter stored in cookies
    # the access token (a string) represents the authorization of a specific application to access specific parts of a user’s data
    token = github.fetch_token("https://github.com/login/oauth/access_token", # token url - OAuth endpoint given in the GitHub API documentation, https://www.oauth.com/oauth2-servers/access-tokens/
                               client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
                               authorization_response=request.url) # the URL github gave to the user to redirect back to your site - this needs to be stored since the access token request must contain the same redirect URL for verification when issuing the access token (https://curity.io/docs/haapi-data-model/latest/oauth-authorization-response.html, https://developer.mozilla.org/en-US/docs/Web/API/Request/url)
    print(request.url)

    response = make_response(redirect(url_for("profile")))
    response.set_cookie("oauth_token", json.dumps(token), httponly=True) # json.dumps() function will convert the python object into a json string

    return response

@app.route("/profile")
def profile():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"), token=json.loads(request.cookies.get("oauth_token"))) # creates AOuth session using the token created before - it tells github that the user has successfully logged in
    github_profile_data = github.get('https://api.github.com/user').json() # the Users API allows to get public and private information about the authenticated user
                                                                           # json() method takes a Response stream, reads it to completion and parses the body text as JSON. it produces a JS object.

    return render_template("profile.html", github_profile_data=github_profile_data)

@app.route("/github/logout")
def logout():
    response = make_response(redirect(url_for('index')))  # redirect to the index page
    response.set_cookie("oauth_token", expires=0)  # delete the oauth_cookie to logout

    return response

if __name__ == "__main__":
    app.run()