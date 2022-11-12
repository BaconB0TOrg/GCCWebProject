import os, enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# String values are persisted to db, not integer values
class RoleEnum(enum.Enum):
  Owner = 1
  Moderator = 2
  Developer = 3
  Member = 4

# make sure table names are correct
class UserServerRole(db.Model):
  __tablename__ = 'user_server_roles'
  id = db.Column(db.Integer, primary_key=True)
  server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  permissions = db.relationship('user_server_role_permssions', backref='user_server_role')

# TODO: Finish a table for Server-Role-Permission, so owners can
#       edit what permissions each role is allowed to do on a per-server
#       basis
class ServerRolePermission(db.Model):
  __tablename__ = 'user_server_role_permssions'
  id = db.Column(db.Integer, primary_key=True)
  server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
  role_id = db.Column(db.Enum(RoleEnum))
  name = db.Column(db.Unicode, nullable=False)
  permission = db.Column(db.Unicode)

# make sure table names are correct
class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  password = db.Column(db.Unicode, nullable=False)
  email = db.Column(db.Unicode, nullable=False)
  username = db.Column(db.Unicode, nullable=False)
  site_role = db.Column(db.Integer, db.ForeignKey('SiteRoles.id'))
  servers = db.relationship('Server', backref='users')

# make sure table names are correct
class Server(db.Model):
  __tablename__ = 'servers'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Unicode, nullable=False)
  # TODO: Finish