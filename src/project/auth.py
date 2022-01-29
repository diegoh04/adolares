from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
import random, string
import re
import datetime
import json

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    """if not current_user.username == "BNA":
        return redirect(url_for('main.micartera'))
        """
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
#@login_required
def signup_post():
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')
    initialbalance = request.form.get('initialbalance')
    noequipo = request.form.get('noequipo')
    
    user = User.query.filter_by(username=username).first() # if this returns a user, then the username already exists in database
    
    # For regex username validation
    reg = r"^[a-zA-Z]*$"
    pat = re.compile(reg)
    mat = re.search(pat, username)

    if user: # if user is found, we want to redirect back to signup page so user can try again
        flash('Username already exists')
        return redirect(url_for('auth.signup'))
    
    if not mat:  # validate user input 
        flash('Username cannot contain spaces or numbers, only letters. Please retry.')
        return redirect(url_for('auth.signup'))

    ct = datetime.datetime.now()
    ct = ct.strftime("%H:%M del %d/%m") 
    tlog = [["receive", f"{username}", f"tu cuenta ha sido creada con ${initialbalance} adolares.", f"{ct}"]]

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(username=username, name=name, password=generate_password_hash(password, method='sha256'), adolares=initialbalance, noequipo=noequipo, transactionlog=json.dumps(tlog))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('main.micartera'))

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    # if the above code check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.micartera'))
