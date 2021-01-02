from flask import Flask
from flask import render_template, session, redirect, request, url_for, flash
from flask_login import (
    UserMixin,
    AnonymousUserMixin,
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from werkzeug.security import generate_password_hash, check_password_hash

import os

from wtforms import Form, PasswordField, StringField, validators
class LoginForm(Form):
    username = StringField('Username', [validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(min=8)])

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.secret_key = os.urandom(16)
login_manager = LoginManager()
login_manager.init_app(app)

from google.cloud import firestore
db = firestore.Client()

class User(UserMixin):
    def __init__(self, *, username, pass_hash, **kwargs):
        self._id = username
        self._pass_hash = pass_hash
        self._kwargs = kwargs

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
        
    def to_dict(self):
        return dict(**self._kwargs, username = self.id, pass_hash = self._pass_hash)
    
    @staticmethod
    def from_dict(kwargs):
        return User(**kwargs)
    

    @staticmethod
    def get(user_id):
        doc_ref = db.collection(u'users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        else:
            raise KeyError(f"User {user_id} does not exist")

        
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    print("Ha")
    if current_user.is_anonymous:
        user_id = "Anon"
    else:
        user_id = current_user.id
    return render_template('main.html', username=user_id)

@login_required
@app.route('/profile/<username>')
def profile(username=None):
    return render_template('main.html', username=username)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if request.method == "GET":
        return render_template('login.html', form=form)       

    if 1: #form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user_id = request.form.get("username")
        try:
            user = User.get(user_id)
        except KeyError:
            flash(f"User {user_id} does not exist")
            return render_template('login.html', form=form)     

        login_user(user)

        flash('Logged in successfully.')
        

        return redirect(url_for('index'))
    return render_template('login.html', form=form)