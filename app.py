import os
import sys

import sqlite3
from sqlite3 import Error
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, login_required

# Configure application
app = Flask(__name__)
app.debug = True

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] ="filesystem"
Session(app)

# Configure database
conn = sqlite3.connect("mytime.db")
conn.execute('''CREATE TABLE IF NOT EXISTS user
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                 username TEXT NOT NULL,
                 hash TEXT NOT NULL);''')
conn.close()

@app.route("/")
def index():
    """ Homepage """
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register """
    if request.method == "GET":
        return render_template("register.html")

    else:
        # Create database connection
        conn = sqlite3.connect("mytime.db")
        cur = conn.cursor()
        username = request.form.get("username")

        if not request.form.get("username"):
            return apology("Enter username")

        # check username available or not
        cur.execute("SELECT username FROM user WHERE username=?", (username,))
        if cur.fetchone() != None:
            return apology("Username is taken")

        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Enter password and confirmation")

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password and confirmation do not match")

        hash_password = generate_password_hash(request.form.get("password"))

        # Add user into database
        cur.execute("INSERT INTO user (username, hash) VALUES (?, ?)", (username, hash_password))
        conn.commit()
        conn.close()
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # Login page
    if request.method == "GET":
        return render_template("login.html")

    else:
        # check username and password
        if not request.form.get("username"):
            return apology("Must provide username")
        elif not request.form.get("password"):
            return apology("Must provide password")

        # Query database for username
        conn = sqlite3.connect("mytime.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE username=?",(request.form.get("username"),))
        rows = cur.fetchone()
        if rows == None:
            return apology("Username does not exists")
        else:
            if not check_password_hash(rows['hash'], request.form.get("password")):
                return apology("Incorrect username and/or password")
        # Remember which user has logged in
        session["user_id"] = rows['id']

        conn.close()
        return render_template("dashboard.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    return redirect("/")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/history")
def history():
    return render_template("history.html")

def errorhandler(e):
    """Handle error """
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
