import os
import models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
  print(dbpath)
  User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  models.init(db, dbpath=dbpath, seed=True) 
