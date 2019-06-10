import sqlite3
from sqlite3 import Error
from flask import render_template, request, session, redirect

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def apology(message):
    return render_template("apology.html", message=message)


