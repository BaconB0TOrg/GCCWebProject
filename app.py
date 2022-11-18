import os
import models
from flask import Flask
from flask import render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.get('/welcome/')
def welcome():
    return render_template("home.html")

@app.get('/login/')
def get_login():
    form = LoginForm()
    return render_template("login.html", form=form)

@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template("register.html", form=form)

@app.post("/login/")
def post_login():
  form = LoginForm()
  if form.validate():
    return redirect(url_for('welcome'))
  else:
    for field,error in form.errors.items():
      flash(f"{field}: {error}")
    return redirect(url_for('get_login'))

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        return redirect(url_for('welcome'))
    else:
        # flash error messages for all validation problems 
        for field,error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

with app.app_context():
  print(dbpath)
  User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  models.init(db, dbpath=dbpath, seed=True) 
