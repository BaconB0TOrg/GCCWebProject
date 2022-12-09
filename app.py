import mc_lib.mcdocker as mcdocker 
import os, models
from flask import Flask, escape
from flask import render_template, url_for, redirect, flash, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import time

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm, ServerForm, ChangeEmailForm, ServerUpdateForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecretkeythatislongenoughcool'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#####
# Utilities
####

def flash_form_errors(form):
  for field,error in form.errors.items():
    flash(f'{field}: {error}')

#########################
# Route Handlers        #
#########################

@app.route('/site-map/')
def site_map():
  links = []
  for rule in app.url_map.iter_rules():
    if 'GET' in rule.methods:
      rule = escape(rule.rule)
      links.append(f'<a href={rule}>{rule}</a>')
  # links is now a list of url's with their parameters
  linksString = '<br>'.join(links)
  return linksString

@app.get('/')
def redirect_to_welcome():
  return redirect('/welcome/')

@app.get('/welcome/')
def welcome():
  user_id = session.get('user-id')
  users = []
  servers = []
  user = None
  if(user_id != None):
    users = User.query.filter_by(id=user_id).all()
    if len(users) != 0:
      servers = Server.query.filter_by(owner_id=user_id).all()
      user = users[0]
      user.servers = servers
      print(user.servers)

  return render_template('home.html', user=user)

@app.get('/login/')
def get_login():
  if session.get('logged-in'):
    flash("You're already logged in!")
    return redirect(url_for('welcome'))
  form = LoginForm()
  return render_template('login.html', form=form)

@app.post('/login/')
def post_login():
  # Don't allow logged in users to nav here
  if session.get('logged-in'):
    print('[INFO] User tried to login while already logged in!')
    print('[INFO] User tried to login while already logged in!')
    flash('You are not allowed to view that page.')
    return redirect(url_for('welcome'))

  form = LoginForm()
  if form.validate():
    # get user if exists and go from there
    username = form.username.data
    user = User.query.filter_by(username=username).first()

    if user == None:
      print(f'[WARN] Failed to login: User {username} does not exist.')
      flash('Incorrect username and/or password combination!')
      return redirect(url_for('get_login'))

    valid = sha256_crypt.verify(str(form.password.data), user.password)
    if not valid:
      print(f'[WARN] Failed to login: Incorrect password for user {username}.')
      flash('Incorrect username and/or password combination!')
      return redirect(url_for('get_login'))

    session['logged-in'] = True
    session['user-email'] = user.email
    session['user-id'] = user.id

    print(f'[INFO] User {user.username} logged in.')
    flash(f'Welcome back, {user.username}!')
    return redirect(url_for('welcome'))
  else:
    print('[INFO] Failed to login user: Invalid form.')
    flash_form_errors(form)
    return redirect(url_for('get_login'))

@app.route('/log-out/')
def get_log_out():
  if request.method != 'GET':
    print(f"[WARN] User tried to {request.method} to {url_for('get_log_out')}. Only GET is allowed")
    flash("You can't do that!")
    return redirect(url_for('welcome'))
  # if you're not logged in, wut
  if not session.get('logged-in'):
    print("[INFO] Anonymous user tried to log out.")
    flash("You're already logged out!")
    return redirect(url_for('welcome'))
  session['logged-in'] = False
  session['user-email'] = None
  session['user-id'] = None

  flash("You've been logged out.")
  return redirect(url_for('welcome'))

@app.get('/account/')
def get_account():
  # if you're not logged in, you can't be here.
  if not session.get('logged-in'):
    print(f'[WARN] Failed to GET {url_for("get_account")}: Anonymous user.')
    flash('You have to be logged in to see that page.')
    return redirect(url_for('get_login'))

  user_id = session['user-id']
  user = User.query.filter_by(id=user_id).first()
  # if user doesn't exist
  if not user:
    print(f"[WARN] Failed to GET {url_for('get_account')}: user {user_id} doesn't exist")
    flash('You have to be logged in to see that page.')
    return redirect(url_for('get_login'))
  
  form = ChangeEmailForm()
  print(f"[INFO] Successfully accessed {url_for('get_account')} for user {user_id}")
  return render_template('account.html', user=user, form=form)

@app.post('/account/change-email/')
def change_email():
  form = ChangeEmailForm()

  if session.get('logged-in') and form.validate_on_submit():
    # valid form. Check if user exists
    user_id = session['user-id']
    user = User.query.filter_by(id=user_id).first()
    if not user:
      flash("You're not allowed to do that!")
      return redirect(url_for('welcome'))

    # update user's email
    user.email = form.email.data
    db.session.add(user)
    db.session.commit()
    flash("Email successfully changed!")
    return redirect(url_for('get_account'))
  else:
    # invalid form
    flash_form_errors(form)
    return redirect(url_for('get_account'))

@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template('register.html', form=form)

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        email = form.email.data
        uname = form.username.data
        checkUsers = User.query.filter_by(email=email).all()
        if len(checkUsers) > 0:
          # email already exists.
          flash('That email is already in use!')
          return redirect(url_for('get_register'))
        checkUsers = User.query.filter_by(username=uname).all()
        if len(checkUsers) > 0:
          # username already exists.
          flash('That username is taken!')
          return redirect(url_for('get_register'))
        # encrypt password.
        pw = sha256_crypt.encrypt(str(form.password.data))
        user = User(password=pw, email=email, username=uname)

        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(email=email).first()

        session['logged-in'] = True
        session['user-email'] = user.email
        session['user-id'] = user.id
        flash(f'Welcome {uname}!')

        return redirect(url_for('welcome'))
    else:
        # flash error messages for all validation problems 
        flash_form_errors(form)
        return redirect(url_for('get_register'))

@app.get('/server/')
def list_server():
  if not session.get('logged-in'):
    flash('You have to be logged in to access that page!')
    return redirect(url_for('get_login'))
  
  email=session.get('user-email')
  user = User.query.filter_by(email=email).first()
  if user == None:
    print("[ERROR]: logged-in token was true but no valid email was saved in the session!")
    flash('Uh oh, your account is unavailable.')
    return redirect(url_for('get_login'))
  servers = Server.query.all()
  # servers = Server.query.filter_by(owner_id=user.id).all()
  return render_template('server_list.html', servers=servers)

@app.get('/server/create/')
def get_create_server():
  if not session.get('logged-in'):
    flash("You need to be logged in to see that page!")
    return redirect(url_for('get_login'))
  form = ServerForm()
  tags = Tag.query.all()

  form.tags.choices = [(t.id, t.name) for t in tags]
  return render_template('new_server.html', form=form)

@app.post('/server/create/')
def post_create_server():
  if not session.get('logged-in'):
    print(f'[INFO] Anonymous user tried to {request.method} {url_for("post_create_server")}')
    flash("You must be logged in to do that!")
    return redirect(url_for('get_login'))

  tags = Tag.query.all()
  form = ServerForm()
  form.tags.choices = [(t.id, t.name) for t in tags]

  if form.validate_on_submit():
    user_id = session.get('user-id')
    user = User.query.filter_by(id=user_id).first()
    if not user:
      print(f"[ERROR] Failed to create server: User {user_id} does not exist")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_login'))

    # this calc won't work if we delete servers who no longer have docker containers from the db.
    port = 25565+Server.query.count()*2
    # TODO: Pass properties here rather than force a separate call.
    docker_id = mcdocker.make_server(name=form.name.data,port=port, max_players=int(form.maxPlayers.data))
    
    if not docker_id:
      print("[CRITICAL] Server could not be created!")
      flash('The server could not be created, please wait before trying again.')
      return redirect(url_for('get_create_server'))

    tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
    server = Server(name=form.name.data, description=str(form.description.data), docker_id=str(docker_id), owner_id=user.id, max_players=int(form.maxPlayers.data), port=port, tags=tags)

    db.session.add(server)
    db.session.commit()
    s = Server.query.filter_by(docker_id=docker_id).first()
    return redirect(url_for('list_server'))
  else:
    flash_form_errors(form)
    return redirect(url_for('get_create_server'))

@app.get('/server/<int:server_id>/')
def show_server(server_id):
  server = Server.query.filter_by(id=server_id).first()
  if not server:
    if not session.get('logged-in'):
      flash("That server doesn't exist! Why not create one? Login to start!")
      return redirect(url_for('get_login'))
    else:
      flash("That server doesn't exist! Why not create one?")
      return redirect(url_for('get_create_server'))
  return render_template('server.html', server=server)

@app.get('/server/<int:server_id>/update/')
def get_update_server(server_id):
  if not session.get('logged-in'):
    print(f'[INFO] Anonymous user tried to {request.method} {url_for("get_update_server")}')
    flash("You must be logged in to do that!")
    return redirect(url_for('get_login'))

  user_id = session.get('user-id')
  user = User.query.filter_by(id=user_id).first()

  if not user:
    print(f"[ERROR] Failed to update server: User {user_id} does not exist")
    flash("You don't have permission to do that!")
    return redirect(url_for('get_login'))
  
  server = Server.query.filter_by(id=server_id).first()
  if not server or server.owner_id != user_id:
    if not server:
      print(f'[WARN] Server {server_id} does not exist.')
    else:
      print(f'[WARN] User {user_id} tried updating Server {server_id}, but does not own it.')
    flash("You don't have permission to do that!")
    return redirect(url_for('list_server'))
  # user exists and is logged in, server exists and is owned by said user.
  # make form with default field values
  form = ServerUpdateForm(
    name=server.name,
    description=server.description,
    tags=server.tags,
    id=server.id
  )
  tags = Tag.query.all()
  form.tags.choices = [(t.id, t.name) for t in tags]
  return render_template('update_server.html', form=form)

@app.post('/server/<int:server_id>/update/')
def post_update_server(server_id):
  if not session.get('logged-in'):
    print(f'[INFO] Anonymous user tried to {request.method} {url_for("post_update_server")}')
    flash("You must be logged in to do that!")
    return redirect(url_for('get_login'))

  form = ServerUpdateForm()
  form.tags.choices = [(t.id, t.name) for t in Tag.query.all()]
  if form.validate_on_submit():
    form_server_id = int(form.id.data)
    if form_server_id != server_id:
      print(f"[WARN] Failed to update server: User {user_id} does not exist")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_login'))

    user_id = session.get('user-id')
    user = User.query.filter_by(id=user_id).first()
    if not user:
      print(f"[WARN] Failed to update server: User {user_id} does not exist")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_login'))

    servers = Server.query.filter_by(owner_id=user_id).all()
    if not servers or len(servers) == 0:
      print(f"[WARN] Failed to update server: User doesn't own any servers!")
      flash("You have to own the server in order to update it!")
      return redirect(url_for('get_create_server'))
    
    server_as_list = list(filter(lambda s : s.id == form_server_id, servers))
    if not server_as_list or len(server_as_list) == 0:
      print(f'[WARN] Failed to update server: User {user_id} does not own Server {server_id}!')
      flash("You have to own the server in order to update it!")
      return redirect(url_for('get_create_server'))

    server = server_as_list[0]
    server.name = form.name.data
    server.description = form.description.data
    tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
    server.tags = tags

    db.session.add(server)
    db.session.commit()
    flash("Update successful!")
    return redirect(url_for('show_server', server_id=server_id))
  else:
    flash_form_errors(form)
    return redirect(url_for('get_update_server'))

@app.get('/server/<int:server_id>/delete')
def delete_server(server_id):
  if not session.get('logged-in'):
    print(f'Anonymous user tried to delete server {server_id}')
    flash("You don't have permission to do that!")
    return redirect(url_for('welcome'))
  
  server = Server.query.filter_by(id=server_id).first()
  if session.get('user-id') == server.owner_id:
    mcdocker.remove_docker(container_id=server.docker_id)
    db.session.delete(server)
    db.session.commit()
    flash('Server succesfully deleted!')
    return redirect(url_for('list_server'))
  else:
    print(f'[WARN] User {session.get("user-id")} tried to delete server {server_id}')
    flash("You don't have permission to do that!")
    return redirect(url_for('list_server'))

@app.get('/server/<int:server_id>/terminal/')
def get_terminal(server_id):
  if server_id == None:
    return redirect('400.html', 400)
  server = Server.query.filter_by(id=server_id).first()
  if not server:
    print(f'Failed to access server {server_id}: Does not exist')
    flash("You don't have permission to do that!")  
    return redirect(url_for('welcome'))
  # TODO: Check userServerRole for permission to access Terminal
  if server.owner_id != int(session.get('user-id')):
    print(f'User {session.get("user-id")} failed to access server {server_id}: Not the owner')
    flash("You don't have permission to do that!") 
    return redirect(url_for('welcome'))
  
  return render_template('terminal.html', docker_id=server.docker_id)

@app.get('/mc_command/')
def mc_command():
  query = request.args
  rcon_response = mcdocker.run_docker_mc_command(query.get('docker-id'), query.get('command'))
  print(rcon_response)
  response = jsonify(message=rcon_response)
  return response

with app.app_context():
  User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  models.init(db, seed=False, tables=(User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent))
