import enum
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

def setup_models(db: SQLAlchemy):
  # Base = declarative_base()
  class UserServerRole(db.Model):
    __tablename__ = 'user_server_roles'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_name = db.Column(db.Unicode, db.ForeignKey('server_role_permissions.role_name'))

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

  class ServerTag(db.Model):
    __tablename__ = 'server_tags'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))

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


  # make sure table names are correct
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

  
  # make sure table names are correct
  class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False)
    username = db.Column(db.Unicode, nullable=False)
    site_role = db.Column(db.Integer, db.ForeignKey(SiteRole.id))
    servers = db.relationship('Server', secondary=UserServerRole, back_populates='users')

  return User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent

########################################################################
#                                   API                                #
########################################################################

def init(db: SQLAlchemy, dbpath: str = None, seed: bool = False):
  print("hi")
  """
  Initializes the database at the given path `dbpath`. By default, no data is inserted
  to the database. `seed=True` will seed the database.
  """
  models_reset(db, seed=seed)
  return True

def models_reset(db: SQLAlchemy, seed: bool=False):
  """Drops all tables and recreates them with. `seed=True` will insert dummy data into the database"""
  db.drop_all()
  db.create_all()
  if seed:
    models_seed(db)

def models_seed(db: SQLAlchemy):
  # TODO: Seed the tables with admin accounts.
  User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = setup_models(db)
  siteRoleOne = SiteRole(name="admin", action="create", resource="server")

  db.session.add(siteRoleOne)
  db.session.commit()
  
  siteRoles = SiteRole.query.all()
  userOne = User(username="admin", email="admin@email.com", password="admin", site_role=siteRoles[0].id)

  db.session.add(userOne)
  db.session.commit()

  print("user added to database")

  tags = [
    Tag(name="SMP"),
    Tag(name="Vanilla"),
    Tag(name="Modded")
  ]
  db.session.add_all(tags)
  db.session.commit()

  users = User.query.all()
  tags = Tag.query.all()

  serverOne = Server(name="First Server!", description="The first server of the Minecraft Server Hosting Service, <cool and memorable name here>!", docker_id="fake docker id", max_players=20, tags=[tags[0], tags[1]])
  db.session.add(serverOne)
  db.session.commit()
  
  # serverRoles = [
  #   ServerRolePermission()
  # ]

  print(f"Implement {__file__}.seed_tables!")
  pass

# String values are persisted to db, not integer values
# may not need this
class DefaultRoleEnum(enum.Enum):
  Owner = 1
  Moderator = 2
  Developer = 3
  Member = 4
  Guest = 5

# make sure table names are correct. 
# This user on this server has this role.



# class ServerTag(db.Model):
#   __tablename__ = 'server_tags'
#   id = db.Column(db.Integer, primary_key=True)
#   tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
#   server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))


# class UserServerRole(db.Model):
#   __tablename__ = 'user_server_roles'
#   server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), primary_key=True)
#   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
#   role_name = db.Column(db.Unicode, db.ForeignKey('server_role_permissions.role_name'), nullable=False)
#   permissions = db.relationship('ServerRolePermission')

# TODO: Finish table for Server-Role-Permission, so owners can
#       edit what permissions each role is allowed to do on a per-server
#       basis
# This role on this server has these permissions.
# serverRolePermission = db.Table(
#   'server_role_permissions',
#   Base.metadata,
#   db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
#   # let users give custom names to roles. 
#   # Also lets them define new roles with different sets of permissions
#   db.Column('role_name', db.Unicode, nullable=False, primary_key=True),
#   # read, write, etc.
#   db.Column('action', db.Unicode, nullable=False),
#   # Server description, server configuration files, etc.
#   db.Column('resource', db.Unicode, nullable=False)
# )
# class ServerRolePermission(db.Model):
#   __tablename__ = 'user_server_role_permissions'
#   server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), primary_key=True)
#   # let users give custom names to roles. 
#   # Also lets them define new roles with different sets of permissions
#   role_name = db.Column(db.Unicode, nullable=False, primary_key=True)
#   # read, write, etc.
#   action = db.Column(db.Unicode, nullable=False)
#   # Server description, server configuration files, etc.
#   resource = db.Column(db.Unicode, nullable=False)

# # make sure table names are correct
# class User(db.Model):
#   __tablename__ = 'users'
#   id = db.Column(db.Integer, primary_key=True)
#   password = db.Column(db.Unicode, nullable=False)
#   email = db.Column(db.Unicode, nullable=False)
#   username = db.Column(db.Unicode, nullable=False)
#   site_role = db.Column(db.Integer, db.ForeignKey('site_roles.id'))
#   servers = db.relationship('Server', secondary=userServerRole, back_populates='users')

# # make sure table names are correct
# class Server(db.Model):
#   __tablename__ = 'servers'
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.Unicode, nullable=False)
#   description = db.Column(db.Unicode, nullable=True) #  nullable!
#   docker_id = db.Column(db.Unicode, nullable=False)
#   max_players = db.Column(db.Integer, nullable=False)
#   users = db.relationship('User', secondary=userServerRole, back_populates='servers')
#   roles = db.relationship('ServerRolePermission', backref='server')
#   events = db.relationship('ServerEvent', backref='sever')
#   tags = db.relationship('Tag', secondary=serverTag, backref='server')

# class SiteRole(db.Model):
#   __tablename__ = 'site_roles',
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.Unicode, nullable=False)
#   # view, create (purchase), etc.
#   action = db.Column(db.Unicode, nullable=False)
#   # Site Dashboard, servers, etc.
#   resource = db.Column(db.Unicode, nullable=False)
#   users = db.relationship('User', backref='site_role')

# class ServerEvent(db.Model):
#   __tablename__ = 'server_events'
#   id = db.Column(db.Integer, primary_key=True)
#   description = db.Column(db.Unicode, nullable=True)
#   name = db.Column(db.Unicode, nullable=False)
#   server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
#   # Maybe no image
#   # img = db.Column

# class Tag(db.Model):
  # __tablename__ = 'tags'
  # id = db.Column(db.Integer, primary_key=True)
  # name = db.Column(db.Unicode, nullable=False)
