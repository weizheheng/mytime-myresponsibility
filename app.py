import os
import sys

import sqlite3
from sqlite3 import Error
from flask import Flask, redirect, render_template, request, session, make_response
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
conn.execute('''CREATE TABLE IF NOT EXISTS task
                (id NOT NULL,
                task1 TEXT, task2 TEXT, task3 TEXT, task4 TEXT, task5 TEXT,
                task6 TEXT, task7 TEXT, task8 TEXT, task9 TEXT, task10 TEXT,
                task11 TEXT, task12 TEXT, task13 TEXT, task14 TEXT, task15 TEXT);''')
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
        return redirect("/planning")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    return redirect("/")

@app.route("/planning", methods=["GET", "POST"])
@login_required
def planning():

    # Get the username using user_id
    if request.method == "GET":

        # Query username from database
        conn = sqlite3.connect("mytime.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT username FROM user WHERE id = ?", (session.get("user_id"),))
        rows = cur.fetchone()
        username = rows['username']
        conn.close()
        return render_template("planning.html", username=username)

    else:
        # Get the data user posted using planning.html (bad design here)
        task1 = request.form.get("t0800")
        task2 = request.form.get("t0900")
        task3 = request.form.get("t1000")
        task4 = request.form.get("t1100")
        task5 = request.form.get("t1200")
        task6 = request.form.get("t1300")
        task7 = request.form.get("t1400")
        task8 = request.form.get("t1500")
        task9 = request.form.get("t1600")
        task10 = request.form.get("t1700")
        task11 = request.form.get("t1800")
        task12 = request.form.get("t1900")
        task13 = request.form.get("t2000")
        task14 = request.form.get("t2100")
        task15 = request.form.get("t2200")
        user_id = session.get("user_id")

        # Insert the data into database table - task
        conn = sqlite3.connect("mytime.db")
        cur = conn.cursor()
        cur.execute('''INSERT INTO task (id, task1, task2, task3, task4, task5,
                        task6, task7, task8, task9, task10, task11, task12,
                        task13, task14, task15) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (user_id,task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14,task15))
        conn.commit()
        conn.close()
        return redirect("/dashboard")


@app.route("/dashboard")
@login_required
def dashboard():
    if request.method == "GET":

        conn=sqlite3.connect("mytime.db")
        conn.row_factory = sqlite3.Row
        cur=conn.cursor()
        cur.execute("SELECT username FROM user WHERE id = ?", (session.get("user_id"),))
        rows = cur.fetchone()
        username = rows['username']
        cur.execute("SELECT * FROM task WHERE id=?", (session.get("user_id"),))
        rows = cur.fetchone()
        conn.close()
        return render_template("dashboard.html", username=username, rows=rows)


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
