import mc_lib.mcdocker as mcdocker
import os, models
from flask import Flask, escape
from flask import render_template, url_for, redirect, flash, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm, ServerForm, ChangeEmailForm

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
    return render_template('home.html')

@app.get('/login/')
def get_login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.post('/login/')
def post_login():
  # Don't allow logged in users to nav here
  if session.get('logged-in'):
    flash('You are not allowed to view that page')
    return redirect(url_for('welcome'))

  form = LoginForm()
  if form.validate():
    # get user if exists and go from there
    username = form.username.data
    user = User.query.filter_by(username=username).first()

    if user == None:
      flash('Incorrect username and/or password combination!')
      return redirect(url_for('get_login'))
    print(user.password)

    valid = sha256_crypt.verify(str(form.password.data), user.password)
    if not valid:
      flash('Incorrect username and/or password combination!')
      return redirect(url_for('get_login'))

    session['logged-in'] = True
    session['user-email'] = user.email
    session['user-id'] = user.id

    flash(f'Welcome back {user.username}')
    return redirect(url_for('welcome'))
  else:
    flash_form_errors(form)
    return redirect(url_for('get_login'))

@app.route('/log-out/')
def get_log_out():
  if request.method != 'GET':
    print(f"User requested {url_for('get_log_out')} with a {request.method} request. Only GET is allowed")
    flash("You can't do that!")
    return redirect(url_for('welcome'))
  # if you're not logged in, wut
  if not session.get('logged-in'):
    print("Anonymous user tried to log out.")
    flash("You can't do that!")
    return redirect(url_for('welcome'))
  session['logged-in'] = False
  session['user-email'] = None
  session['user-id'] = None

  flash("You've been logged out.")
  return redirect(url_for('welcome'))

@app.get('/account/')
def get_account():
  # if you're not logged in, you can't be here.
  if not session.get('logged-in') and session.get('user-id'):
    flash('You are not allowed to view that page')
    return redirect(url_for('welcome'))

  user_id = session['user-id']
  user = User.query.filter_by(id=user_id).first()
  # if user doesn't exist
  if not user:
    flash('You are not allowed to view that page')
    return redirect(url_for('welcome'))
  
  form = ChangeEmailForm()
  return render_template('account.html', user=user, form=form)

@app.post('/account/change-email/')
def change_email():
  form = ChangeEmailForm()

  if session.get('logged-in') and session.get('user-id') and form.validate_on_submit():
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

@app.get('/server/<int:server_id>/')
def show_server(server_id):
  server = Server.query.filter_by(id=server_id).first()
  return render_template('server.html', server=server)

@app.get('/server/<int:server_id>/delete')
def delete_server(server_id):
  server = Server.query.filter_by(id=server_id).first()
  mcdocker.remove_docker(container_id=server.docker_id)
  db.session.delete(server)
  db.session.commit()
  return redirect('/server/')

@app.get('/server/')
def list_server():
  sf = ServerForm()
  # do something to make sure users can't edit their token
  # and be logged in to someone else's account.
  loggedIn=session.get('logged-in')
  if not loggedIn:
    flash('You have to be logged in to access that page!')
    return redirect('/login/')
  
  email=session.get('user-email')
  user = User.query.filter_by(email=email).first()
  if user == None:
    flash('You have to be logged in to access that page!')
    return redirect('/login/')
  servers = Server.query.filter_by(owner_id=user.id).all()
  return render_template('server.html', form=sf, servers=servers)

@app.post('/server/')
def post_server():
  sf = ServerForm()
  if sf.validate_on_submit():
    numPortsUsed = Server.query.count()
    email = session.get('user-email')
    user = User.query.filter_by(email=email).first()
    # this calc won't work if we delete servers who no longer have docker containers from the db.
    docker_id = mcdocker.make_server(name=sf.name.data,port=25565+numPortsUsed*2)
    # TODO: Make max_players configurable by the user to some upper limit
    if not docker_id:
      flash('The server could not be created, please wait before trying again.')
      return redirect(url_for('list_server'))
    server = Server(name=sf.name.data, docker_id=str(docker_id), owner_id=user.id, max_players=20)
    print(server)
    db.session.add(server)
    db.session.commit()
    s = Server.query.filter_by(docker_id=docker_id).first()
    return redirect(url_for('list_server'))
  else:
    flash_form_errors(sf)
  return redirect(url_for('list_server'))

@app.get('/terminal/<int:server_id>')
def get_terminal(server_id):
  if server_id == None:
    return redirect('400.html', 400)
  # TODO: Don't assume it exists, bad
  server = Server.query.filter_by(id=server_id).first()
  print(server)
  
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
