import enum
import os
from passlib.hash import sha256_crypt
import mc_lib.mcdocker as mcdocker
import flask_login
from collections import namedtuple

from flask_sqlalchemy import SQLAlchemy

class TableModels:
  def __init__(self, db: SQLAlchemy, seed: bool = False):
    existing_tables = [table for table in db.metadata.tables.values()]
    if(len(existing_tables) != 0):
      # make logging a separate module
      if(os.getenv('log_level') in ['debug', 'warn', 'error']):
        print("[ERROR]: Tables for this databse are already defined!")
      raise Exception("TableModles should not be instantiated more than once with the same SQLAlchemy database object.")
    
    #### Declare Instance Attributes ####

    self.db = db                # the database used for this instance
    # self.UserServerRole       # The UserServerRole table
    #      ServerEvent          # The ServerEvent table
    #      Tag                  # The Tag table
    #      ServerTag            # The ServerTag table
    #      ServerRolePermission # The ServerRolePermission table
    #      Server               # The Server table
    #      SiteRole             # The SiteRole table
    #      User                 # The User table
    #      DefaultRoleEnum      # Role keys for the webapp itself.
    #      tables               # The list of tables in this instance.


    # String values are persisted to db, not integer values
    # may not need this
    class DefaultRoleEnum(enum.Enum):
      Owner = 1
      Moderator = 2
      Developer = 3
      Member = 4
      Guest = 5

    #### Instance variables #### 
    
    UserServerRole, ServerEvent, Tag, ServerTag, ServerRolePermission, Server, SiteRole, User = self.__defineTables(db)
    self.UserServerRole = UserServerRole
    self.ServerEvent = ServerEvent
    self.Tag = Tag
    self.ServerTag = ServerTag
    self.ServerRolePermission = ServerRolePermission
    self.Server = Server
    self.SiteRole = SiteRole
    self.User = User
    self.DefaultRoleEnum = DefaultRoleEnum

    Tables = namedtuple("Tables", ['UserServerRole', 'ServerEvent', 'Tag', 'ServerTag', 'ServerRolePermission', 'Server', 'SiteRole', 'User'])
    self.tables = Tables(UserServerRole, ServerEvent, Tag, ServerTag, ServerRolePermission, Server, SiteRole, User)

    #### Create Database and Seed Data ####

    self.reset()
    if seed:
      self.seed_optional()

    ######## END __init__ ########

  #########################
  #          API          #
  #########################

  def reset(self) -> None:
    """Drops all tables and recreates them while also seeding required data into them."""
    # TODO: remove all docker containers!
    self.db.drop_all()
    self.db.create_all()
    self.seed_required()

  # Seeds tables needed by prod and dev
  def seed_required(self) -> None:
    """Seeds the minimum required data into the database."""
    Tag = self.Tag
    tags = [
      Tag(name="SMP"),
      Tag(name="Vanilla"),
      # Tag(name="Modded"),
      Tag(name="Friendly"),
      Tag(name="Community"),
      Tag(name="FFA"),
      Tag(name="Chaos"),
      Tag(name="Factions"),
      Tag(name="New Players"),
      Tag(name="Experienced Players"),
      Tag(name="Hardcore"),
      Tag(name="Keep Inventory"),
      Tag(name="Roleplay"),
      Tag(name="AutoFarms"),
      Tag(name="Builders")
    ]
    self.db.session.add_all(tags)
    self.db.session.commit()

  # seeds tables that are not required by prod nor dev
  def seed_optional(self) -> None:
    """Seeds the database with extra, non-essential data. Primarily used for testing or demos."""
    User, Server, Tag = self.User, self.Server, self.Tag

    # TODO: Seed the tables with admin accounts.
    # User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = setup_models(db)
    # siteRoleOne = SiteRole(name="admin", action="create", resource="server")

    # db.session.add(siteRoleOne)
    # db.session.commit()
    
    # siteRoles = SiteRole.query.all()
    addUsers = [
      User(username="Mario", email="chrispratt@gmail.com", password=sha256_crypt.hash(str("itsamemario"))),
      User(username="BaconB0T", email="brown1ethan@gmail.com", password=sha256_crypt.hash(str("12345678"))),
      User(username="username", email="email@provider.com", password=sha256_crypt.hash(str("12345678")))
    ]
    # userOne = User(username="admin", email="admin@email.com", password="admin", site_role_id=siteRoles[0].id)

    self.db.session.add_all(addUsers)
    self.db.session.commit()

    users = User.query.all()
    tags = Tag.query.all()

    # Make docker containers
    docker_ids = [
      mcdocker.make_server(name="FirstServer",port=25565, max_players=20),
      # mcdocker.make_server(name="SecondServer",port=25567,max_players=10),
      # mcdocker.make_server(name="ThirdServer",port=25569, max_players=20)
      # mcdocker.make_server(name="FourthServer",port=25571,max_players=20),
      # mcdocker.make_server(name="FifthServer",port=25573, max_players=50),
      # mcdocker.make_server(name="SixthServer",port=25575, max_players=2)
    ]

    addServers = [
      Server(name="FirstServer", port=25565,owner_id=users[0].id,docker_id=docker_ids[0], description="The First server of the Minecraft Server Hosting Service, <cool and memorable name here>!",  max_players=20, tags=[tags[0], tags[1]]),
      Server(name="SecondServer",port=25567,owner_id=users[0].id, docker_id=docker_ids[1], description="The Second server of the Minecraft Server Hosting Service, <cool and memorable name here>!",max_players=10, tags=[tags[2]]),
      # Server(name="ThirdServer", port=25569,owner_id=users[1].id,docker_id=docker_ids[2], description="The Third server of the Minecraft Server Hosting Service, <cool and memorable name here>!",  max_players=20, tags=[tags[0]])
      # Server(name="FourthServer",owner_id=users[2].id, docker_id=docker_ids[3], description="The Fourth server of the Minecraft Server Hosting Service, <cool and memorable name here>!",max_players=20, tags=[tags[0], tags[1], tags[2], tags[3]]),
      # Server(name="FifthServer", owner_id=users[3].id,docker_id=docker_ids[4], description="The Fifth server of the Minecraft Server Hosting Service, <cool and memorable name here>!",  max_players=50, tags=[tags[5], tags[4]]),
      # Server(name="SixthServer", owner_id=users[2].id,docker_id=docker_ids[5], description="The Sixth server of the Minecraft Server Hosting Service, <cool and memorable name here>!",  max_players=2,  tags=[tags[6], tags[9]])
    ]
    self.db.session.add_all(addServers)
    self.db.session.commit()
    
    # serverRoles = [
    #   ServerRolePermission()
    # ]

    print(f"Finish {self.__class__}.seed_tables!")

  def seed_tests(self, server=False) -> None:
    """Seeds data for tests. Inputs less than seed_optional"""
    User, Server, Tag = self.User, self.Server, self.Tag
    user = User(username="test", email="test@test.com", password=sha256_crypt.hash(str("password")))
    self.db.session.add(user)
    self.db.session.commit()

    user = User.query.get(1)
    tags = Tag.query.all()

    if server:
      name='testName'
      container_id = mcdocker.make_server(name=name,port=25565, max_players=20)

      server = Server(name=name, port=25565, owner_id=user.id, docker_id=container_id, description="Test description",  max_players=20, tags=[tags[0], tags[1]])
      self.db.session.add(server)
      self.db.session.commit()

  @property
  def get_tables(self) -> tuple:
    """Returns a named tuple containing the tables defined in this instance, accessible by their names:
    - UserServerRole: The UserServerRole table
    - ServerEvent: The ServerEvent table
    - Tag: The Tag table
    - ServerTag: The ServerTag table
    - ServerRolePermission: The ServerRolePermission table
    - Server: The Server table
    - SiteRole: The SiteRole table
    - User: The User table"""
    return self.tables

  def __defineTables(self, db: SQLAlchemy):
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
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"ServerEvent(name={self.name}, description={self.description}, server_id={self.server_id})"
      # Maybe no image
      # img = db.Column

    class Tag(db.Model):
      __tablename__ = 'tags'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.Unicode, nullable=False, unique=True)
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"Tag(name={self.name}, id={self.id})"

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
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"ServeRolePermission(role_name={self.role_name}, action={self.action}, resource={self.resource}, server_id={self.server_id})"

    # Make a server properties model & store them here with a ref to the server object
    class Server(db.Model):
      __tablename__ = 'servers'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.Unicode, nullable=False)
      description = db.Column(db.Unicode, nullable=True) #  nullable!
      docker_id = db.Column(db.Unicode, nullable=False, unique=True)
      max_players = db.Column(db.Integer, nullable=False)
      port = db.Column(db.Integer, nullable=False, unique=True)
      owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
      status = db.Column(db.Boolean, nullable=False, default=False)
      users = db.relationship('User', secondary=UserServerRole, back_populates='servers')
      roles = db.relationship(ServerRolePermission, backref='server')
      events = db.relationship(ServerEvent, backref='sever')
      tags = db.relationship('Tag', secondary=ServerTag, backref='server')
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"Server(name={self.name}, status={self.status}, description={self.description}, owner_id={self.owner_id}, num_users={len(self.users)}, tags={self.tags}, docker_id={self.docker_id})"

    class SiteRole(db.Model):
      __tablename__ = 'site_roles'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.Unicode, nullable=False, unique=True)
      # view, create (purchase), etc.
      action = db.Column(db.Unicode, nullable=False)
      # Site Dashboard, servers, etc.
      resource = db.Column(db.Unicode, nullable=False)
      users = db.relationship('User', backref='site_role')
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"SiteRole(name={self.name}, action={self.action}, resource={self.resource})"

    class User(db.Model, flask_login.UserMixin):
      __tablename__ = 'users'
      id = db.Column(db.Integer, primary_key=True)
      password = db.Column(db.Unicode, nullable=False)
      email = db.Column(db.Unicode, nullable=False, unique=True)
      username = db.Column(db.Unicode, nullable=False, unique=True)
      # TODO: Make site role mandatory
      site_role_id = db.Column(db.Integer, db.ForeignKey(SiteRole.id))
      servers = db.relationship('Server', secondary=UserServerRole, back_populates='users')
      
      def get_id(self):
        return str(self.id)

      @property
      def is_authenticated(self):
        return self.is_active

      @property
      def is_anonymous(self):
        if id:
          return True
        else:
          return False

      @property
      def is_active(self):
        # TODO: implement email validation
        return True
        
      def __repr__(self):
        return str(self)
      def __str__(self):
        return f"User(username={self.username}, email={self.email}, password=[REMOVED], site_role_id={self.site_role_id})"
    
    return UserServerRole, ServerEvent, Tag, ServerTag, ServerRolePermission, Server, SiteRole, User
