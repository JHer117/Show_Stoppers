from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from MySQLconnection import connectToMySQL
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "GandorfTheGer"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SESSION_KEY = "user_id"
if __name__=="__main__":
    app.run(debug=True)