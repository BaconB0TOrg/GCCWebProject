from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length

class LoginForm(FlaskForm):
    username = StringField("Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    username = StringField("Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    confirm_email = EmailField("Confirm Email", validators=[InputRequired(), Email(), EqualTo('email', message="Email addresses Do Not Match.")] )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords Do Not Match.")])
    submit = SubmitField("Submit")
    
class ServerForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    tags = SelectField("Tags")
    maxPlayers = IntegerField("Maximum Players", validators=[InputRequired()])
    OwnerID = IntegerField("Owner ID", validators=[InputRequired()])
    DockerID = IntegerField("Docker ID", validators=[InputRequired()])
    submit = SubmitField("Submit")