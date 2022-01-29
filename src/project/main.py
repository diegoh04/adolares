from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, jsonify, send_file
from . import db
from flask_login import login_required, current_user
from .models import User
import datetime
import json
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

marketIsClosed = False
@main.before_request
def checkMarket():
    global marketIsClosed

    if marketIsClosed and request.path != url_for('main.marketdown') and request.path != url_for('auth.login'):
        try:
            if current_user.username != "BNA":
                return redirect(url_for('main.marketdown'))
        except:
            return redirect(url_for('main.marketdown'))

    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        
            


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.micartera'))
    else:
        return render_template('index.html')

@main.route('/micartera')
@login_required
def micartera():
    tlog = json.loads(current_user.transactionlog)
    return render_template('micartera.html', name=current_user.name, adolares=current_user.adolares, username=current_user.username, noequipo=current_user.noequipo, tlog=reversed(tlog), mantenimiento=marketIsClosed)

@main.route('/micartera', methods=['POST'])
@login_required
def micartera_post():
    newowner = request.form.get('newowner')
    newuser = User.query.filter_by(username=newowner).first()
    quantity = int(request.form.get('quantity'))

    # Check that newowner user exists
    if not newuser:
        flash('Usuario no existe!')
        return redirect(url_for('main.micartera') + "#sendmodal")

    # Check that user doesn't try to send money to himself
    elif current_user == newuser:
        flash('No te puedes mandar dinero a ti mismo!')
        return redirect(url_for('main.micartera') + "#sendmodal")

    # We confirm the user has sufficient funds to procede with the operation
    elif current_user.adolares < quantity:
        flash('Fondos insuficientes!')
        return redirect(url_for('main.micartera') + "#sendmodal")

    # We confirm quantity transferred is not negative
    elif quantity < 0:
        flash('No se puede mandar dinero en negativo!')
        return redirect(url_for('main.micartera') + "#sendmodal")
    
    #If so, we remove the requested money from the current_user and asign it to the newowner
    else:
        #Actual transaction
        current_user.adolares = current_user.adolares - quantity
        newuser.adolares = newuser.adolares + quantity
        #Transaction log
        ct = datetime.datetime.now()
        ct = ct.strftime("%H:%M del %d/%m") 

        cutlog = json.loads(current_user.transactionlog)
        cutlog.append(["send", f"{newuser.name}", f"Tú le mandaste ${quantity} adolares a", f"{ct}"])
        current_user.transactionlog = json.dumps(cutlog)

        nutlog = json.loads(newuser.transactionlog)
        nutlog.append(["receive", f"{current_user.name}", f"te envió ${quantity} adolares", f"{ct}"])
        newuser.transactionlog = json.dumps(nutlog)
        #Commit database
        db.session.commit()
        
    return redirect(url_for('main.micartera'))

@main.route('/updateQuantity', methods=['POST'])
@login_required
def updateQuantity():
    update = request.get_json()
    res = make_response(jsonify(current_user.adolares), 200)
    return res

@main.route("/sqlite")
@login_required
def sqlite():
    path = "db.sqlite"
    return send_file(path, as_attachment=True)

@main.route('/sqliteupload', methods=['POST'])
def sqliteupload():
    file = request.files['database']
    if file:
        file.save(os.path.join("project", file.filename))

    return redirect(url_for('main.micartera'))

@main.route('/marketdown')
def marketdown():
    global marketIsClosed
    if marketIsClosed:
        return render_template('marketdown.html')
    else:
        return redirect(url_for('main.micartera'))

@main.route('/mantenimiento', methods=['POST'])
def mantenimiento():
    wishto = request.form.get('wishto')
    global marketIsClosed

    if wishto == "True":
        marketIsClosed = True

    elif wishto == "False":
        marketIsClosed = False

    return redirect(url_for('main.micartera'))