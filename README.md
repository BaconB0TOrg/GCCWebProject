# GCCWebProject

Minecraft Server Hosting for GCC's Web Development class

# Docker Container Setup

### Need to have docker desktop installed and running in the background <br> Install docker py package: `py -m pip install docker`

# Starting the Server

Clone repo

#### Dependencies

`python -m pip install flask docker flask-sqlalchemy Flask-WTF email_validator passlib Flask-Login`<br>
`python -m pip install -e .`<br>
`python -m pip install -r requirements-dev.txt`<br>

## Run this 

Start the server using `python -m flask --app "app.py" run` and visit localhost:5000 to see it.

# Development

## Flask-Login

- To access the currently signed-in user, use current_user.
- All templates have access to current_user automagically, no need to pass it into render_template.
- 4 functions are added to the User model that are required by Flask-Login (_These can be accessed via current_user as well as any User object._):
  - `is_authenticated` returns whether the current user is authenticated or not.
  - `is_anonymouse` returns whether the current user is anonymous or authenticated.
    - unsure how this is different from [is_authenticated](#flask-login), but whatever.
  - `is_active` just returns `True` for now, but will in the future check if the user has validated their email and return true if so and false if not.
  - `get_id`. :)