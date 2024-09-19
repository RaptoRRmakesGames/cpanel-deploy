# Import the Flask class from the flask module
from flask import (
    Flask,
    render_template,
    get_flashed_messages,
    flash,
    session,
    request,
    redirect,
    url_for,
    jsonify,
    make_response,
    send_file,
)
from datetime import timedelta, datetime

import db

import json

import time

from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

from io import BytesIO

import pandas as pd 

# import pandas as pd

# from io import BytesIO

# Create an instance of the Flask class
app = Flask(__name__)


app.config["SECRET_KEY"] = "very_secret_key_12351232"

app.config.update(SESSION_PERMANENT=True, SESSION_TYPE="filesystem")

def auth():
    if "auth" in session:
        return session["auth"]
    else:
        return False


def admin():

    if auth():
        return session["user_admin"]
    else:
        return False


def get_next_seven_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    next_seven_days = [
        (start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(8)
    ][0:7]
    return next_seven_days


@app.before_request
def before_request_func():

    session["start"] = time.time()

    if "user_id" in session:
        db.USER_ID = session["user_id"]

    if "auth" in session and session["auth"]:

        dbe, c = db.connect()
        stuff = []
        c.execute("SELECT * FROM employees WHERE user_id = %s", [session["user_id"]])
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM titles WHERE user_id = %s", [session["user_id"]])
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM sub_department WHERE user_id = %s", [session["user_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM big_kitchens WHERE user_id = %s", [session["user_id"]]
        )
        stuff.append(c.fetchall())
        c.execute(
            "SELECT * FROM large_department WHERE user_id = %s", [session["user_id"]]
        )
        stuff.append(c.fetchall())
        c.execute("SELECT * FROM programs WHERE user_id = %s", [session["user_id"]])
        stuff.append(c.fetchall())



        session["hide_edit"] = False
        for thing in stuff:
            if len(thing) > 0:
                break

        else:
            session["hide_edit"] = True
            


@app.after_request
def after_request_func(response):

    if __name__ == "__main__":
        print(time.time() - session["start"])
        
    return response