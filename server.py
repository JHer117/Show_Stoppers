from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from MySQLconnection import connectToMySQL
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "TenaciousJHJW"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SESSION_KEY = "user_id"
@app.route("/")
def initial():
    return render_template("main.html")
@app.route("/login", methods=['POST'])
def login():
    is_valid = True
    if not EMAIL_REGEX.match(request.form['email']) or len(request.form['email']) > 255:
        is_valid = False
        flash("Please enter a valid email.")
    if len(request.form['pw']) < 1 or len(request.form['pw']) > 255:
        is_valid = False
        flash("Please enter a valid password.")
    if is_valid == True:
        mysql = connectToMySQL("ShowStoppers")
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            "email": request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password']
            if bcrypt.check_password_hash(hashed_password, request.form['pw']):
                session['user_id'] = user[0]['id']
                return redirect("/ShowStoppers")
            else:
                flash("Password is invalid.")
                return redirect("/")
    return redirect("/")
@app.route("/registration", methods=['POST'])
def registration():
    fnis_valid = False           
    lnis_valid = False
    emis_valid = False
    pwis_valid = False
    if len(request.form['fname']) > 1:
        if len(request.form['fname']) < 256:
            if request.form['fname'].isalpha():
                fnis_valid = True
    if len(request.form['lname']) > 1:
        if len(request.form['lname']) < 256:
            if request.form['lname'].isalpha():
                lnis_valid = True
    if len(request.form['email']) > 1:
        if len(request.form['email']) < 256:
            if EMAIL_REGEX.match(request.form['email']):
                emis_valid = True
    if len(request.form['pw']) > 4:
        if request.form['pw'] == request.form['con_pw']:
            pwis_valid = True
    if fnis_valid and lnis_valid and emis_valid and pwis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW());"
        data = {
            "fn": request.form['fname'],
            "ln": request.form['lname'],
            "em": request.form['email'],
            "pw": bcrypt.generate_password_hash(request.form['pw']),
        }
        user_id = mysql.query_db(query, data)
        session[SESSION_KEY] = user_id
        return redirect("/ShowStoppers")
    elif fnis_valid and lnis_valid and emis_valid:
        flash ("Your password was invalid. All passwords must be over 5 characters.")
    elif fnis_valid and lnis_valid and pwis_valid:
        flash ("Your email was invalid.")
    elif fnis_valid and emis_valid and pwis_valid:
        flash ("Your last name was invalid.")
    elif lnis_valid and emis_valid and pwis_valid:
        flash ("Your first name was invalid.")
    elif fnis_valid and lnis_valid:
        flash ("Your email and password were invalid. Remember all passwords must be over 5 characters.")
    elif fnis_valid and emis_valid:
        flash ("Your last name and password were invalid. Remember all passwords must be over 5 characters.")
    elif fnis_valid and pwis_valid:
        flash ("Your last name and email were invalid.")
    elif lnis_valid and emis_valid:
        flash ("Your first name and password were invalid. Remember all passwords must be over 5 characters.")
    elif lnis_valid and pwis_valid:
        flash ("Your first name and email were invalid.")
    elif emis_valid and pwis_valid:
        flash ("Your first name and last name were invalid.")
    elif fnis_valid:
        flash ("Your last name, email, and password were invalid. Remember all passwords must be over 5 characters.")
    elif lnis_valid:
        flash ("Your first name, email, and password were invalid. Remember all passwords must be over 5 characters.")
    elif emis_valid:
        flash ("Your first name, last name, and password were invalid. Remember all passwords must be over 5 characters.")
    elif pwis_valid:
        flash ("Your first name, last name, and email were invalid.")
    else:
        flash ("None of your information was valid, please resubmit.")
    return redirect("/")
@app.route("/ShowStoppers")
def acct():
    if "user_id" not in session:
        return redirect("/")
    mysql = connectToMySQL("ShowStoppers")
    query = "SELECT users.first_name, users.last_name, users.id FROM users WHERE users.id = %(users_id)s"
    data = {
        "users_id": session['user_id']
    }
    user = mysql.query_db(query, data)
    mysql = connectToMySQL("ShowStoppers")
    query = "SELECT users.id, users.first_name, users.last_name, attendedgigs.id AS attended_gig_id, attendedgigs.attendedGig, shows.id AS shows_id, shows.start_time, shows.end_time, band.title, venue.location FROM users JOIN attendedgigs ON users.id = attendedgigs.users_id LEFT JOIN shows ON attendedgigs.shows_id = shows.id LEFT JOIN band ON shows.band_id=band.id LEFT JOIN venue ON shows.venue_id=venue.id WHERE users.id = %(users_id)s"
    attended_gigs = mysql.query_db(query, data)
    session['user_id']
    print(user)
    return render_template("account.html", user=user[0], attended_gigs=attended_gigs)
@app.route("/rsvp_to_gig/<attended_gig_id>")
def rsvp(attended_gig_id):
    mysql = connectToMySQL("ShowStoppers")
    query = "UPDATE attendedgigs SET attendedgigs.attendedGig = TRUE WHERE attendedgigs.id = %(attended_gig_id)s"
    data = {
        "attended_gig_id": attended_gig_id,
    }
    mysql.query_db(query, data)
    return redirect("/ShowStoppers")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/edit/<user_id>/info")
def editInfo(user_id):
    mysql = connectToMySQL("ShowStoppers")
    query = "SELECT * FROM users WHERE users.id = %(data_id)s"
    data = {
        "data_id": session[SESSION_KEY],
    }
    user = mysql.query_db(query, data)
    session['user_id']
    return render_template("edit_accnt.html", user=user[0])
@app.route("/edit/<user_id>/update", methods=['POST'])
def updateInfo(user_id):
    if SESSION_KEY not in session:
        return redirect("/ShowStoppers")
    fnis_valid = False
    lnis_valid = False
    emis_valid = False
    if request.form['fname'].isalpha():
        if len(request.form['fname']) < 256 and len(request.form['fname']) > 0:
            fnis_valid = True
    if request.form['lname'].isalpha():
        if len(request.form['lname']) < 256 and len(request.form['lname']) > 0:
            lnis_valid = True
    if EMAIL_REGEX.match(request.form['email']) and len(request.form['email']) < 256:
        emis_valid = True
    if fnis_valid and lnis_valid and emis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(email)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "fn": request.form['fname'],
            "ln": request.form['lname'],
            "email": request.form['email'],
        }
        flash ("First name, last name, and email updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif fnis_valid and lnis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "fn": request.form['fname'],
            "ln": request.form['lname'],
        }
        flash ("First name and last name updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif fnis_valid and emis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET first_name = %(fn)s, email = %(email)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "fn": request.form['fname'],
            "email": request.form['email'],
        }
        flash ("First name and email updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif lnis_valid and emis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET last_name = %(ln)s, email = %(email)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "ln": request.form['lname'],
            "email": request.form['email'],
        }
        flash ("Last name and email updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif fnis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET first_name = %(fn)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "fn": request.form['fname'],
        }
        flash ("First name updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif lnis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET last_name = %(ln)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "ln": request.form['lname'],
        }
        flash ("Last name updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    elif emis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "UPDATE users SET email = %(email)s, updated_at = NOW() WHERE id = %(uid)s"
        data = {
            "data_id": session[SESSION_KEY],
            "uid": user_id,
            "email": request.form['email'],
        }
        flash ("Email updated.")
        mysql.query_db(query, data)
        return redirect("/edit/" + user_id + "/info")
    return redirect("/edit/" + user_id + "/info")
@app.route("/edit/<user_id>/pwupdate", methods=['POST'])
def updatePW(user_id):
    if SESSION_KEY not in session:
        return redirect("/ShowStoppers")
    opwis_valid = False
    npwis_valid = False
    if len(request.form['old_pw']) > 0:
        opwis_valid = True
    if request.form['pw'] == request.form['con_pw']:
        if len(request.form['pw']) > 4:
            npwis_valid = True
    if opwis_valid and npwis_valid:
        mysql = connectToMySQL("ShowStoppers")
        query = "SELECT * FROM users WHERE id = %(id)s"
        data = {
        "id": session['user_id']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password']
            if bcrypt.check_password_hash(hashed_password, request.form['old_pw']):
                new_pw_hash = bcrypt.generate_password_hash(request.form['pw'])
                mysql = connectToMySQL("ShowStoppers")
                query = "UPDATE users SET password = %(pw)s, updated_at = NOW() WHERE id = %(uid)s"
                data = {
                "uid": user_id,
                "pw": new_pw_hash,
                }
                flash ("Password change succeeded.")
                mysql.query_db(query, data)
                return redirect("/edit/" + user_id + "/info")
        else:
            flash("Password is invalid.")
            return redirect("/edit/" + user_id + "/info")
    flash ("Password change failed.")
    return redirect("/edit/" + user_id + "/info")
@app.route("/gigs")
def gigs():
    if SESSION_KEY not in session:
        return redirect("/")
    mysql = connectToMySQL("ShowStoppers")
    query = "SELECT shows.*, band.title, venue.location FROM shows LEFT JOIN band ON shows.band_id=band.id LEFT JOIN venue ON shows.venue_id=venue.id;"
    bandN = mysql.query_db(query)
    session.get('user_id')
    print(session.get('user_id'))
    print(bandN)
    return render_template("gigs.html", shows = bandN)
@app.route("/gig_Select", methods=['POST'])
def gigSelect():
    if SESSION_KEY not in session:
        return redirect("/")
    mysql = connectToMySQL("ShowStoppers")
    query = "SELECT * FROM attendedGigs WHERE (shows_id = %(sid)s AND users_id = %(uid)s)"
    data = {
        "sid": int(request.form['mainID']),
        "uid": session.get('user_id'),
    }
    attended_gigs = mysql.query_db(query, data)
    if not attended_gigs:
        mysql = connectToMySQL("ShowStoppers")
        query = "INSERT INTO attendedGigs (shows_id, users_id, attendedGig) VALUES  (%(sid)s, %(uid)s, 0)"
        mysql.query_db(query, data)
        flash("Data Successful")
    return redirect("/gigs")
if __name__=="__main__":
    app.run(debug=True)