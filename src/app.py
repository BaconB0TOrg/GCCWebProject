from forms import LoginForm, RegisterForm, ServerForm, ChangeEmailForm, ServerUpdateForm, is_safe_url, CreateServerForm
import mc_lib.mcdocker as mcdocker
import os
from models import TableModels
from flask import Flask, escape, abort, request, render_template, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from passlib.hash import sha256_crypt

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'somesecretkeythatislongenoughcool'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "get_login"

#########################
#      Utilities        #
#########################

def flash_form_errors(form):
  for field, error in form.errors.items():
    flash(f'{field}: {error}')

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

def safe_redirect(form, next, path):
  if not is_safe_url(next):
    if next != None:
      print(f'[INFO] Blocked redirect to foreign url: {next} on {path}. Redirecting to welcome page.')
    return form.redirect('welcome')

  return form.redirect(next)

#########################
#    Route Handlers     #
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
  return render_template('home.html')

@app.get('/login/')
def get_login():
  if current_user.is_authenticated:
    flash("You're already logged in!")
    return redirect(url_for('welcome'))
  form = LoginForm()
  return render_template('login.html', form=form)

@app.post('/login/')
def post_login():
  # Don't allow logged in users to nav here
  form = LoginForm()

  if current_user.is_authenticated:
    print(
        f'[INFO] User {current_user.id} tried to login while already logged in!')
    flash('You must logout before you can login as someone else!')
    
    next = request.args.get('next')

    return safe_redirect(form, next, '/login/')
  if form.validate_on_submit():
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

    login_user(user)
    print(f'[INFO] User {user.id} logged in.')
    flash(f'Welcome back, {user.username}!')

    next = request.args.get('next')

    return safe_redirect(form, next, '/login/')
  else:
    print('[INFO] Failed to login user: Invalid form.')
    flash_form_errors(form)
    return redirect(url_for('get_login'))

@app.route('/logout/')
def get_logout():
  if not current_user.is_authenticated:
    flash("You can't do that.")
    return redirect(url_for('welcome'))
  logout_user()
  flash("You've been logged out.")
  return redirect(url_for('welcome'))

@app.get('/account/')
@login_required
def get_account():
  form = ChangeEmailForm()
  print(f"[INFO] Accessed {url_for('get_account')} for user {-1}")
  return render_template('account.html', form=form)

@app.post('/account/change-email/')
@login_required
def change_email():
  form = ChangeEmailForm()

  if form.validate_on_submit():
    # valid form. Check if user exists
    # update user's email
    user = current_user
    user.email = form.email.data
    db.session.add(user)
    db.session.commit()
    # user = User.query.get(user.id)
    login_user(user)
    # TODO: Validate new email
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
  if form.validate_on_submit():
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

    pw = sha256_crypt.hash(str(form.password.data))
    user = User(password=pw, email=email, username=uname)

    db.session.add(user)
    db.session.commit()

    user = User.query.filter_by(email=email).first()
    login_user(user)

    flash(f'Welcome {uname}!')
    next = request.args.get('next')

    return safe_redirect(form, next, '/register/')
  else:
    # flash error messages for all validation problems
    flash_form_errors(form)
    return redirect(url_for('get_register'))

@app.get('/servers/')
def list_server():
  # TODO: Paginate servers index
  servers = Server.query.all()
  return render_template('server_list.html', servers=servers)

@app.get('/servers/create/')
@login_required
def get_create_server():
  form = ServerForm()
  tags = Tag.query.all()

  form.tags.choices = [(t.id, t.name) for t in tags]
  return render_template('server_creation.html', form=form)

@app.post('/servers/create/')
@login_required
def post_create_server():
  tags = Tag.query.all()
  form = CreateServerForm()
  form.tags.choices = [(t.id, t.name) for t in tags]

  if form.validate_on_submit():
    user_id = current_user.id
    user = User.query.get(user_id)
    if not user:
      print(f"[ERROR] Failed to create server: User {user_id} does not exist")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_login'))

    # this calc won't work if we delete servers who no longer have docker containers from the db.
    port = 25565+Server.query.count()*2
    # TODO: Pass properties here rather than force a separate call.
    docker_id = mcdocker.make_server(name=form.server_name.data,port=port, max_players=str(form.number_of_players.data), gamemode=str(form.gamemode.data.lower()))
    
    if not docker_id:
      print("[CRITICAL] Server could not be created!")
      flash('The server could not be created, please wait before trying again.')
      return redirect(url_for('get_create_server'))

    tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
    server = Server(name=form.server_name.data, description=str(form.server_description.data), docker_id=str(docker_id), owner_id=user.id, max_players=int(form.number_of_players.data), port=port, tags=tags)

    db.session.add(server)
    db.session.commit()
    s = Server.query.filter_by(docker_id=docker_id).first()
    # TODO: Shouldn't this redirect to show_server?
    return redirect(url_for('list_server'))
  else:
    flash_form_errors(form)
    return redirect(url_for('get_create_server'))

@app.get('/servers/<int:server_id>/')
def show_server(server_id):
  server = Server.query.get(server_id)
  if not server:
    if not (current_user and current_user.is_authenticated):
      flash("That server doesn't exist! Why not create one? Login to start!")
      return redirect(url_for('get_login'))
    else:
      flash("That server doesn't exist! Why not create one?")
      return redirect(url_for('get_create_server'))

  if current_user.is_authenticated and (current_user.id == server.owner_id):
    return render_template('user_server.html', server=server, edit=False)

  return render_template('server.html', server=server)

@app.get('/servers/<int:server_id>/update/')
@login_required
def get_update_server(server_id):
  server = Server.query.get(server_id)
  if not server or server.owner_id != current_user.id:
    if not server:
      print(f'[WARN] Server {server_id} does not exist.')
    else:
      print(
          f'[WARN] User {current_user.id} tried updating Server {server_id}, but does not have permission to do so.')
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

@app.post('/servers/<int:server_id>/update/')
@login_required
def post_update_server(server_id):
  form = ServerUpdateForm()
  form.tags.choices = [(t.id, t.name) for t in Tag.query.all()]
  if form.validate_on_submit():
    form_server_id = int(form.id.data)
    if form_server_id != server_id:
      print(f"[WARN] Failed to update server: User {current_user.id} does not exist")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_login'))

    servers = Server.query.filter_by(owner_id=current_user.id).all()
    if not servers or len(servers) == 0:
      print(f"[WARN] Failed to update server: User {current_user.id} doesn't own any servers!")
      flash("You don't have permission to do that.")
      return redirect(url_for('get_create_server'))

    server_as_list = list(filter(lambda s: s.id == form_server_id, servers))
    if not server_as_list or len(server_as_list) == 0:
      print(
          f'[WARN] Failed to update server: User {current_user.id} does not own Server {server_id}!')
      flash("You don't have permission to do that.")
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
    return redirect(url_for('get_update_server', server_id=server_id))

@app.get('/servers/<int:server_id>/delete/')
@login_required
def delete_server(server_id):
  server = Server.query.get(server_id)
  # TODO: Don't assume the server exists
  if current_user.id == server.owner_id:
    mcdocker.remove_docker(container_id=server.docker_id)
    db.session.delete(server)
    db.session.commit()
    flash('Server succesfully deleted!')
    return redirect(url_for('list_server'))
  else:
    print(
        f'[WARN] User {current_user.id} tried to delete server {server_id}')
    flash("You don't have permission to do that!")
    return redirect(url_for('list_server'))

@app.get('/servers/<int:server_id>/terminal/')
@login_required
def get_terminal(server_id):
  if server_id == None:
    return redirect('400.html', 400)
  server = Server.query.get(server_id)
  if not server:
    print(
        f'User {current_user.id} failed to access server {server_id}: Does not exist')
    flash("You don't have permission to do that!")
    return redirect(url_for('welcome'))
  # TODO: Check userServerRole for permission to access Terminal
  if server.owner_id != int(current_user.id):
    print(
        f'User {current_user.id} failed to access server {server_id}: Not the owner')
    flash("You don't have permission to do that!")
    return redirect(url_for('welcome'))

  return render_template('terminal.html', docker_id=server.docker_id)

@app.get('/mc_command/')
@login_required
def mc_command():
  query = request.args
  rcon_response = mcdocker.run_docker_mc_command(
      query.get('docker-id'), query.get('command'))
  print(rcon_response)
  response = jsonify(message=rcon_response)
  return response


with app.app_context():
  # These are accessible because this block runs in the global namespace (the namespace of the
  # app.py module). Thus, these are defined 'global' to this module.
  # This is an indented block of code, but it is not a function nor class definition, so
  # it runs global to the module! I get it! (See the documentation (https://docs.python.org/3/tutorial/classes.html#scopes-and-namespaces-example)
  # for more info)
  tableModels = TableModels(db)
  UserServerRole, ServerEvent, Tag, ServerTag, ServerRolePermission, Server, SiteRole, User = tableModels.tables
