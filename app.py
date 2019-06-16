import os
import sys
import datetime

import sqlite3
from sqlite3 import Error
from flask import Flask, redirect, render_template, request, session, make_response, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import login_required, apology

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
database = "mytime.db"
conn = sqlite3.connect(database)
conn.execute('''CREATE TABLE IF NOT EXISTS user
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                 username TEXT NOT NULL,
                 hash TEXT NOT NULL);''')
conn.execute('''CREATE TABLE IF NOT EXISTS task
                (id INTEGER NOT NULL, date DATE, score INTEGER DEFAULT 0,
                task1 TEXT, task2 TEXT, task3 TEXT, task4 TEXT, task5 TEXT,
                task6 TEXT, task7 TEXT, task8 TEXT, task9 TEXT, task10 TEXT,
                task11 TEXT, task12 TEXT, task13 TEXT, task14 TEXT, task15 TEXT,
                cb1 TEXT DEFAULT '', cb2 TEXT DEFAULT '', cb3 TEXT DEFAULT '', cb4 TEXT DEFAULT '',
                cb5 TEXT DEFAULT '', cb6 TEXT DEFAULT '', cb7 TEXT DEFAULT '', cb8 TEXT DEFAULT '',
                cb9 TEXT DEFAULT '', cb10 TEXT DEFAULT '', cb11 TEXT DEFAULT '',
                cb12 TEXT DEFAULT '', cb13 TEXT DEFAULT '', cb14 TEXT DEFAULT '',
                cb15 TEXT DEFAULT '', ta1 TEXT DEFAULT '', ta2 TEXT DEFAULT '',
                ta3 TEXT DEFAULT '', ta4 TEXT DEFAULT '', ta5 TEXT DEFAULT '',
                ta6 TEXT DEFAULT '', ta7 TEXT DEFAULT '', ta8 TEXT DEFAULT '',
                ta9 TEXT DEFAULT '', ta10 TEXT DEFAULT '', ta11 TEXT DEFAULT '',
                ta12 TEXT DEFAULT '', ta13 TEXT DEFAULT '', ta14 TEXT DEFAULT '',
                ta15 TEXT DEFAULT '');''')
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
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        username = request.form.get("username")

        if not request.form.get("username"):
            flash(u"Please enter username.", 'danger')
            return redirect("/register")

        # check username available or not
        cur.execute("SELECT username FROM user WHERE username=?", (username,))
        if cur.fetchone() != None:
            flash(u"Sorry, the username is not available.", 'danger')
            return redirect("/register")

        if not request.form.get("password") or not request.form.get("confirmation"):
            flash(u"Please enter both password and confirmation fields.", 'danger')
            return redirect("/register")

        if request.form.get("password") != request.form.get("confirmation"):
            flash(u"Password and confirmation do not match.", 'danger')
            return redirect("/register")

        hash_password = generate_password_hash(request.form.get("password"))

        # Add user into database
        cur.execute("INSERT INTO user (username, hash) VALUES (?, ?)", (username, hash_password))
        conn.commit()
        conn.close()
        flash(u"Account registered successfully",'primary')
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():


    # Login page
    if request.method == "GET":
        return render_template("login.html")

    else:
        # check username and password
        if not request.form.get("username"):
            flash(u"Must provide username", 'danger')
            return redirect("/login")
        elif not request.form.get("password"):
            flash(u"Must provide password", 'danger')
            return redirect("/login")

        # Query database for username
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE username=?",(request.form.get("username"),))
        rows = cur.fetchone()
        if rows == None:
            flash(u"Username does not exists, please register here.", 'danger')
            return redirect("/register")
        else:
            if not check_password_hash(rows['hash'], request.form.get("password")):
                flash(u"Incorrect username and/or password.", 'danger')
                return redirect("/login")
        # Remember which user has logged in
        session["user_id"] = rows['id']
        date = datetime.datetime.now().date()


        # Pick which site to go depends on whether the user has or has not plan for the day
        cur.execute("SELECT * FROM task WHERE id=? AND date=?", (session.get("user_id"),date))
        rows = cur.fetchone()
        conn.close()
        if rows == None:
            return redirect("/planning")
        else:
            return redirect("/dashboard")

@app.route("/check")
def check():
    if request.method == "GET":
        date = datetime.datetime.now().date()
        condition = request.args.get("condition")
        cb_id = request.args.get("id")
        ta_id = request.args.get("ta")
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        if condition == "true":
            score = 1
            checkbox = "checked"
            textarea = "readonly"
            cur.execute("UPDATE task SET {}=?, {}=?, score=score+? WHERE id=? AND date=?".format(cb_id, ta_id),
            (checkbox, textarea, score, session.get("user_id"), date))
            conn.commit()
            conn.close()
            return redirect("/dashboard")
        else:
            score = -1
            checkbox = ""
            textarea = ""
            cur.execute("UPDATE task SET {}=?, {}=?, score=score+? WHERE id=? AND date=?".format(cb_id, ta_id),
                         (checkbox, textarea, score, session.get("user_id"), date))
            conn.commit()
            conn.close()
            return redirect("/dashboard")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    return redirect("/")

@app.route("/reset" ,methods=["GET","POST"])
def reset():
    # Reset password
    if request.method == "GET":
        return render_template("reset.html")

    else:
        # check user input for username
        if not request.form.get("username"):
            flash(u"Please enter username", 'danger')
            return redirect("/reset")

        # check username exists in database
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT username FROM user WHERE username=?", (request.form.get("username"),))
        rows = cur.fetchone()
        if rows == None:
            flash(u"Sorry, the username does not exists", 'danger')
            return redirect("/reset")

        # Check user input for password
        if not request.form.get("password") or not request.form.get("confirmation"):
            flash(u"Please enter both password and confirmation fields", 'danger')
            return redirect("/reset")

        # Check password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            flash(u"Make sure the new password and confirmation match", 'danger')
            return redirect("/reset")

        # Passes everything now update new password into database
        hash_password = generate_password_hash(request.form.get("password"))
        cur.execute("UPDATE user set hash=? WHERE username=?",
                    (hash_password, request.form.get("username")))
        conn.commit()
        conn.close()

        flash(u"Password changed successfully!", 'primary')
        return redirect("/login")


@app.route("/planning", methods=["GET", "POST"])
@login_required
def planning():

    # Get the username using user_id
    if request.method == "GET":

        # Query username from database
        conn = sqlite3.connect(database)
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
        date = datetime.datetime.now().date()

        # Insert the data into database table - task
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT * FROM task WHERE id=? AND date=?", (session.get("user_id"),date))
        checking = cur.fetchone()
        if checking == None:
            cur.execute('''INSERT INTO task (id,date, task1, task2, task3, task4, task5,
                        task6, task7, task8, task9, task10, task11, task12,
                        task13, task14, task15) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (user_id, date, task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14,task15))
            conn.commit()
            conn.close()
            return redirect("/dashboard")
        else:
            flash(u"You have already planned your day, update them instead!", 'primary')
            return redirect("/dashboard")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "GET":

        date = datetime.datetime.now().date()
        conn=sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cur=conn.cursor()
        cur.execute("SELECT username FROM user WHERE id = ?", (session.get("user_id"),))
        rows = cur.fetchone()
        username = rows['username']
        cur.execute("SELECT * FROM task WHERE id=? and date=?", (session.get("user_id"), date))
        rows = cur.fetchone()
        conn.close()
        if rows == None:
            flash(u"You haven't plan your day yet", 'danger')
            return redirect("/planning")
        else:
            return render_template("dashboard.html", username=username, rows=rows)

    else:
        # Handle condition when user wants to update their tasks of the same day
        date = datetime.datetime.now().date()
        conn=sqlite3.connect(database)
        conn.row_factory=sqlite3.Row
        cur=conn.cursor()
        cur.execute("SELECT username FROM user WHERE id=?", (session.get("user_id"),))
        rows = cur.fetchone()
        username = rows['username']
        cur.execute("SELECT * FROM task WHERE id=? AND date=?",
                    (session.get("user_id"), date))

        rows = cur.fetchone()
        if rows == None:
            return redirect("/planning")
        else:
            task1 = request.form.get("ta1")
            task2 = request.form.get("ta2")
            task3 = request.form.get("ta3")
            task4 = request.form.get("ta4")
            task5 = request.form.get("ta5")
            task6 = request.form.get("ta6")
            task7 = request.form.get("ta7")
            task8 = request.form.get("ta8")
            task9 = request.form.get("ta9")
            task10 = request.form.get("ta10")
            task11 = request.form.get("ta11")
            task12 = request.form.get("ta12")
            task13 = request.form.get("ta13")
            task14 = request.form.get("ta14")
            task15 = request.form.get("ta15")
            user_id = session.get("user_id")
            cur.execute('''UPDATE task SET task1=?,task2=?,task3=?,task4=?,task5=?,task6=?,task7=?,
                            task8=?, task9=?,task10=?,task11=?,task12=?,task13=?,task14=?,task15=?
                            WHERE id=? AND date=?''',
                            (task1,task2,task3,task4,task5,task6,task7,task8,task9,task10,task11,task12,task13,task14,task15,user_id,date))
            conn.commit()
            cur.execute("SELECT * FROM task WHERE id=? AND date=?",
                        (session.get("user_id"),date))
            rows = cur.fetchone()
            conn.close()
            return render_template("dashboard.html", username=username, rows=rows)

@app.route("/summary", methods=["POST", "GET"])
@login_required
def summary():
    if request.method == "POST":
        conn = sqlite3.connect(database)
        conn.row_factory =sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT date, score FROM task WHERE id=?", (session.get("user_id"),))
        rows = cur.fetchall()
        conn.close()
        return render_template("summary.html", rows=rows)
    else:
        conn = sqlite3.connect(database)
        conn.row_factory =sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT date, score FROM task WHERE id=?", (session.get("user_id"),))
        rows = cur.fetchall()
        conn.close()
        return render_template("summary.html", rows=rows)

@app.route("/history")
def history():
    date = request.args.get("date")
    conn =sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT username FROM user WHERE id=?", (session.get("user_id"),))
    rows = cur.fetchone()
    username = rows['username']
    cur.execute("SELECT * FROM task WHERE id=? AND date=?", (session.get("user_id"), date))
    rows = cur.fetchone()
    conn.close()
    return render_template("history.html", rows=rows, date=date, username=username)

def errorhandler(e):
    """Handle error """
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)
# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
