import mc_lib.mcdocker as mcdocker
import os, models
from flask import Flask, escape
from flask import render_template, url_for, redirect, flash, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')

from forms import LoginForm, RegisterForm, ServerForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "somesecretkeythatislongenoughcool"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#####
# Utilities
####

def flash_form_errors(form):
  for field,error in form.errors.items():
    flash(f"{field}: {error}")

#########################
# Route Handlers        #
#########################

@app.route("/site-map/")
def site_map():
  links = []
  for rule in app.url_map.iter_rules():
    if "GET" in rule.methods:
      rule = escape(rule.rule)
      links.append(f"<a href={rule}>{rule}</a>")
  # links is now a list of url's with their parameters
  linksString = '<br>'.join(links)
  return linksString

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

@app.post("/login/")
def post_login():
  # TODO: Don't allow logged in users to nav here
  form = LoginForm()
  if form.validate():
    # get user if exists and go from there
    username = form.username.data
    user = User.query.filter_by(username=username).first()

    if user == None:
      flash("Incorrect username and/or password combination!")
      return redirect(url_for('get_login'))
    print(user.password)

    valid = sha256_crypt.verify(str(form.password.data), user.password)
    if not valid:
      flash("Incorrect username and/or password combination!")
      return redirect(url_for('get_login'))
    flash(f"Welcome back {user.username}")
    return redirect(url_for('welcome'))
  else:
    flash_form_errors(form)
    return redirect(url_for('get_login'))

@app.get('/register/')
def get_register():
    form = RegisterForm()
    return render_template("register.html", form=form)

@app.post('/register/')
def post_register():
    form = RegisterForm()
    if form.validate():
        email = form.email.data
        uname = form.username.data
        checkUsers = User.query.filter_by(email=email).all()
        if len(checkUsers) > 0:
          # email already exists.
          flash("That email is already in use!")
          return redirect(url_for('get_regiser'))
        checkUsers = User.query.filter_by(username=uname).all()
        if len(checkUsers) > 0:
          # username already exists.
          flash("That username is taken!")
          return redirect(url_for('get_regiser'))
        # encrypt password.
        pw = sha256_crypt.encrypt(str(form.password.data))
        user = User(password=pw, email=email, username=uname)

        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(email=email).first()

        session['logged-in'] = True
        session['user-email'] = user.email
        flash(f"Welcome {uname}!")

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
    server = Server(name=sf.name.data, docker_id=docker_id, owner_id=user.id, max_players=20)
    db.session.add(server)
    db.session.commit()
    s = Server.query.filter_by(docker_id=docker_id).first()
    return redirect(f'/server/')
  else:
    for (k, v) in sf.errors.items():
      flash(f"{k}: {v}")
  return redirect('/server/')

@app.get('/terminal/<int:server_id>')
def get_terminal(server_id):
  if server_id == None:
    return redirect('400.html', 400)
  # TODO: Don't assume it exists, bad
  server = Server.query.filter_by(id=server_id).first()
  
  return render_template('terminal.html', docker_id=server.docker_id)

@app.get('/mc_command/')
def mc_command():
  query = request.args
  rcon_response = mcdocker.run_docker_mc_command(query.get('docker-id'), query.get("command"))
  print(rcon_response)
  response = jsonify(message=rcon_response)
  return response

with app.app_context():
  print(dbpath)
  #User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  #models.init(db, dbpath=dbpath, seed=True) 
  User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent = models.setup_models(db)
  models.init(db, seed=False, tables=(User, Server, Tag, SiteRole, ServerTag, ServerRolePermission, UserServerRole, ServerEvent))
