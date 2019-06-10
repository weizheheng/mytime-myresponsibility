from flask import render_template, request, session, redirect


def apology(message):
    return render_template("apology.html", message=message)

