# GCCWebProject

Minecraft Server Hosting for GCC's Web Development class

# Docker Container Setup

### Need to have docker desktop installed and running in the background <br> Install docker py package: *py -m pip install docker*

# Starting the Server

Clone repo

#### Dependencies

`python -m pip install flask docker flask-sqlalchemy Flask-WTF email_validator passlib`<br>
`python -m pip install -e .`<br>
`python -m pip install -r requirements-dev.txt`<br>

## Run this 

Start the server using `python -m flask --app "app.py" run` and visit localhost:5000 to see it.
