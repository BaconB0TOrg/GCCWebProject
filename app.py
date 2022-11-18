import mc_lib.mcdocker as mcdocker
import os
import sys
import models
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
  print(dbpath)
  #User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  #models.init(db, dbpath=dbpath, seed=True) 


@app.get('/terminal/')
def get_terminal():
  return render_template('terminal.html')

@app.get('/mc_command/')
def mc_command():
  query = request.args
  print(query.get("command"))
  rcon_response = mcdocker.run_docker_mc_command("mc", query.get("command", "Sorry foo"))
  print(rcon_response)
  response = jsonify(message=rcon_response)
  return response




