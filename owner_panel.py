from table_creation import app, auth, admin, get_next_seven_days

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

@app.route('/login_as/<ide>')
def login_as(ide):
    
    user = db.User(ide)
    
    if user.hotel_owner and session['user_preview_mode']:
        session["auth"] = True
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email
        session["user_role"] = user.role
        session["user_admin"] = user.admin
        session["user_owner"] = user.owner
        session["user_hotel_owner"] = user.hotel_owner
        session["parent_id"] = user.parent_id
        session['user_preview_mode'] = False
        return redirect(url_for("manage_users_admin"))
    
    if str(user.parent_id) != str(session['user_id']) :
        print(user.parent_id, type(user.parent_id), type(session['user_id']))
        flash('Cant Login As A User That Isnt Yours!')
        return redirect(url_for('manage_users_admin'))
    
    flash("Login Successful!")
    session["auth"] = True
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session["user_role"] = user.role
    session["user_admin"] = user.admin
    session["user_owner"] = user.owner
    session["user_hotel_owner"] = user.hotel_owner
    session["parent_id"] = user.parent_id

    session['user_preview_mode'] = True
    
    print(session["user_preview_mode"])
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login_page():

    match request.method:

        case "POST":
            user = db.User.login(request.form.get("email"), request.form.get("pass"))
            if isinstance(user, db.User):
                flash("Login Successful!")
                session["auth"] = True
                session["user_id"] = user.id
                session["user_name"] = user.name
                session["user_email"] = user.email
                session["user_role"] = user.role
                session["user_admin"] = user.admin
                session["user_owner"] = user.owner
                session["user_hotel_owner"] = user.hotel_owner
                session["parent_id"] = user.parent_id
                session['user_preview_mode'] = False
                
                print(session["user_hotel_owner"])

                return redirect(url_for("index"))

            else:
                flash(user)
                return redirect(url_for("login_page"))

        case "GET":

            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    # return redirect(url_for("index"))
    if not admin():
        return redirect(url_for("login_page"))

    match request.method:

        case "GET":

            return render_template("register.html", session=session)

        case "POST":

            name = request.form.get("name")
            role = request.form.get("role")
            email = request.form.get("email")
            password = request.form.get("name")
            is_admin = {True: 1, False: 0}[request.form.get("is_admin") == "on"]

            if not db.User.check_email_valid(email):

                flash("Email is not Valid or already in Use!")
                return redirect(url_for("edit_objects"))

            db.User.register_user(
                name, role, email, password, is_admin,0 ,0, session["user_id"]
            )

            flash(f"User `{name}` Succesfully Created!")

            return redirect(url_for("edit_objects"))


@app.route("/logout")
def logout():

    session.clear()

    session["start"] = time.time()

    flash("Successfully Logged Out!")

    return redirect(url_for("login_page"))

@app.route('/owner/add_user', methods=['GET', 'POST'])
def add_user():
    
    match request.method:
        
        case 'GET':
            
            return render_template('add_user_owner.html')
        
        case 'POST':
            
            name = request.form.get("name")
            role = request.form.get("role")
            email = request.form.get("email")
            password = request.form.get("name")
            is_admin = {True: 1, False: 0}[request.form.get("is_admin") == "on"]
            is_hotel_owner = {True: 1, False: 0}[request.form.get("is_hotel_admin") == "on"]

            if not db.User.check_email_valid(email):

                flash("Email is not Valid or already in Use!")
                return redirect(url_for("edit_objects"))

            db.User.register_user(
                name, role, email, password, is_admin, is_hotel_owner, 0, ''
            )

            
            return redirect(url_for('add_user'))

@app.route('/owner/manage_users')
def manage_users():
    
    dbe, c = db.connect()
    
    c.execute('SELECT id FROM users WHERE id=parent_id')
    
    parent_users = [db.User(ide[0]) for ide in c.fetchall()]
    user_dict = []
    
    for parent in parent_users:
        
        c.execute('SELECT * FROM users WHERE id!=parent_id AND parent_id=%s', [parent.id])
        
        user_dict.append((parent, [db.User(ide[0]) for ide in c.fetchall()]))
    
    print(user_dict)
    
    return render_template('manage_users_owner.html', users=user_dict)

@app.route('/admin/manage_users')
def manage_users_admin():
    
    dbe, c = db.connect()
    
    c.execute('SELECT id FROM users WHERE parent_id=%s AND id=parent_id', [session['parent_id']])
    
    parent_users = [db.User(ide[0]) for ide in c.fetchall()]
    user_dict = []
    
    for parent in parent_users:
        
        c.execute('SELECT * FROM users WHERE id!=parent_id AND parent_id=%s', [parent.id])
        
        user_dict.append((parent, [db.User(ide[0]) for ide in c.fetchall()]))
    
    print(user_dict)
    
    return render_template('manage_users_owner.html', users=user_dict)

@app.route('/owner/delete_user/<ide>')
def delete_user(ide):
    
    dbe,c= db.connect()
    
    c.execute('DELETE FROM users WHERE id=%s', [ide])
    
    dbe.commit()
    
    return redirect(url_for('manage_users'))
