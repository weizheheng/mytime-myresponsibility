from flask import render_template, request, session, redirect
from functools import wraps


def apology(message):
    return render_template("apology.html", message=message)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
