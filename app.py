import mc_lib.mcdocker as mcdocker
import os, sys, models, json
from flask import Flask
from flask import render_template, url_for, redirect, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm, ServerForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "somesecretkeythatislongenoughcool"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.get('/')
def redirect_to_welcome():
  return redirect('/welcome/')

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
    # get user if exists and go from there
    return redirect(url_for('welcome'))
  else:
    for field,error in form.errors.items():
      flash(f"{field}: {error}")
    return redirect(url_for('get_login'))

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        # TODO: save to db
        return redirect(url_for('welcome'))
    else:
        # flash error messages for all validation problems 
        for field,error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for('get_register'))

@app.get('/server/')
def get_server():
  sf = ServerForm()
  return render_template('server.html', form=sf)

@app.post('/server/')
def post_server():
  sf = ServerForm()
  if sf.validate_on_submit():
    numPortsUsed = Server.query.count()
    docker_id = mcdocker.make_server(name=sf.name.data,port=25565+numPortsUsed*2)
    # TODO: Make max_players configurable by the user to some upper limit
    server = Server(name=sf.name.data, docker_id=docker_id, max_players=20)
    db.session.add(server)
    db.session.commit()
    s = Server.query.filter_by(docker_id=docker_id).first()
    return redirect(f'/terminal/{s.id}')
  else:
    for (k, v) in sf.errors.items():
      flash(f"{k}: {v}")
  return redirect('/server/')


@app.get('/terminal/<int:serverId>')
def get_terminal(serverId):
  if serverId == None:
    return redirect('400.html', 400)
  # Assumes it exists, which is bad
  server = Server.query.filter_by(id=serverId).first()
  
  return render_template('terminal.html', docker_id=server.docker_id)

@app.get('/mc_command/')
def mc_command():
  query = request.args
  rcon_response = mcdocker.run_docker_mc_command(query.get('docker-id'), query.get("command"))
  print(rcon_response)
  response = jsonify(message=rcon_response)
  return response

UserServerRole = db.Table(
  'user_server_roles',
  db.Column('id', db.Integer, primary_key=True),
  db.Column('server_id', db.Integer, db.ForeignKey('servers.id')),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
  db.Column('role_name', db.Unicode, db.ForeignKey('server_role_permissions.role_name'))
)

class ServerEvent(db.Model):
  __tablename__ = 'server_events'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.Unicode, nullable=True)
  name = db.Column(db.Unicode, nullable=False)
  server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
  # Maybe no image
  # img = db.Column

class Tag(db.Model):
  __tablename__ = 'tags'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Unicode, nullable=False)

ServerTag = db.Table(
  'server_tags',
  db.Column('id', db.Integer, primary_key=True),
  db.Column('server_id', db.Integer, db.ForeignKey('servers.id')),
  db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class ServerRolePermission(db.Model):
  __tablename__ = 'server_role_permissions'
  id = db.Column(db.Integer, primary_key=True)
  server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
  # let users give custom names to roles. 
  # Also lets them define new roles with different sets of permissions
  role_name = db.Column(db.Unicode, nullable=False)
  # read, write, etc.
  action = db.Column(db.Unicode, nullable=False)
  # Server description, server configuration files, etc.
  resource = db.Column(db.Unicode, nullable=False)

class Server(db.Model):
  __tablename__ = 'servers'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Unicode, nullable=False)
  description = db.Column(db.Unicode, nullable=True) #  nullable!
  docker_id = db.Column(db.Unicode, nullable=False)
  max_players = db.Column(db.Integer, nullable=False)
  users = db.relationship('User', secondary=UserServerRole, back_populates='servers')
  roles = db.relationship(ServerRolePermission, backref='server')
  events = db.relationship(ServerEvent, backref='sever')
  tags = db.relationship('Tag', secondary=ServerTag, backref='server')

class SiteRole(db.Model):
  __tablename__ = 'site_roles'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Unicode, nullable=False)
  # view, create (purchase), etc.
  action = db.Column(db.Unicode, nullable=False)
  # Site Dashboard, servers, etc.
  resource = db.Column(db.Unicode, nullable=False)
  users = db.relationship('User', backref='site_role')

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  password = db.Column(db.Unicode, nullable=False)
  email = db.Column(db.Unicode, nullable=False)
  username = db.Column(db.Unicode, nullable=False)
  site_role_id = db.Column(db.Integer, db.ForeignKey(SiteRole.id))
  servers = db.relationship('Server', secondary=UserServerRole, back_populates='users')

with app.app_context():
  print(dbpath)
  #User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  #models.init(db, dbpath=dbpath, seed=True) 
  # User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  models.init(db, seed=False, tables=(User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent))
  # siteRoleOne = SiteRole(name="admin", action="create", resource="server")

  # db.session.add(siteRoleOne)
  # db.session.commit() 
