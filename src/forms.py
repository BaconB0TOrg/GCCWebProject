from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, HiddenField, TextAreaField, SelectField, SelectMultipleField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, EqualTo, Email, Length, Optional, NumberRange
from wtforms.widgets import Select

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    confirm_email = EmailField("Confirm Email", validators=[InputRequired(), Email(), EqualTo('email', message="Email addresses Do Not Match.")] )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords Do Not Match.")])
    submit = SubmitField("Submit")

# This is depreciated don't use it
class ServerForm(FlaskForm):
    server_properties = [
        "level-seed",
        "gamemode",
        "enable-command-block",
        "generator-settings",
        "level-name",
        "motd",
        "pvp",
        "generate-structures",
        "max-chained-neighbor-updates",
        "difficulty",
        "require-resource-pack",
        "max-players",
        "online-mode",
        "enable-status",
        "allow-flight",
        "view-distance",
        "resource-pack-prompt",
        "allow-nether",
        "sync-chunk-writes",
        "op-permission-level",
        "hide-online-players",
        "resource-pack",
        "entity-broadcast-range-percentage",
        "simulation-distance",
        "player-idle-timeout",
        "force-gamemode",
        "rate-limit",
        "hardcore",
        "white-list",
        "broadcast-console-to-ops",
        "spawn-npcs",
        "previews-chat",
        "spawn-animals",
        "function-permission-level",
        "level-type",
        "text-filtering-config",
        "spawn-monsters",
        "enforce-whitelist",
        "spawn-protection",
        "resource-pack-sha1",
        "max-world-size"
    ]
    name = StringField("Name", validators=[InputRequired()])
    description = StringField("Description", validators=[Optional()])
    tags = SelectMultipleField("Tags", validators=[Optional()], coerce=int)
    maxPlayers = IntegerField("Maximum Players", validators=[InputRequired(), NumberRange(2, 50)])
    gamemode = SelectField("Gamemode", choices=[('survival', 'Survival'), ('creative', 'Creative')], validators=[InputRequired()])
    submit = SubmitField("Submit")
    
class ServerUpdateForm(FlaskForm):
    server_properties = [
        "level-seed",
        "gamemode",
        "enable-command-block",
        "generator-settings",
        "level-name",
        "motd",
        "pvp",
        "generate-structures",
        "max-chained-neighbor-updates",
        "difficulty",
        "require-resource-pack",
        "max-players",
        "online-mode",
        "enable-status",
        "allow-flight",
        "view-distance",
        "resource-pack-prompt",
        "allow-nether",
        "sync-chunk-writes",
        "op-permission-level",
        "hide-online-players",
        "resource-pack",
        "entity-broadcast-range-percentage",
        "simulation-distance",
        "player-idle-timeout",
        "force-gamemode",
        "rate-limit",
        "hardcore",
        "white-list",
        "broadcast-console-to-ops",
        "spawn-npcs",
        "previews-chat",
        "spawn-animals",
        "function-permission-level",
        "level-type",
        "text-filtering-config",
        "spawn-monsters",
        "enforce-whitelist",
        "spawn-protection",
        "resource-pack-sha1",
        "max-world-size"
    ]
    name = StringField("Name", validators=[InputRequired()])
    description = StringField("Description", validators=[Optional()])
    tags = SelectMultipleField("Tags", validators=[Optional()], coerce=int)
    id = HiddenField("Id", validators=[InputRequired()])
    submit = SubmitField("Submit")

class ChangeEmailForm(FlaskForm):
    email = EmailField("New Email", validators=[InputRequired(), Email()])
    submit = SubmitField("Change email")

class CreateServerForm(FlaskForm):
    # Selecting tags
    tags = SelectMultipleField("Tags", validators=[Optional()], coerce=int)
    submit = SubmitField("Create")

    # Selecting Server Options TODO: Find out what is going to go in advanced options
    number_of_players = IntegerField("Max Players", validators=[InputRequired(), NumberRange(2, 100)])
    gamemode = SelectField("Gamemode", choices=[('survival', 'Survival'), ('creative', 'Creative')], validators=[InputRequired()])
    difficulty = SelectField("Difficulty", choices=[('peaceful', 'Peaceful'), ('easy', 'Easy'), ('normal', 'Normal'), ('hard', 'Hard')])
    pvp = BooleanField("Player vs. Player", validators=[Optional()])
    '''Advanced options'''
    hardcore = BooleanField("Hardcore", validators=[Optional()])
    spawn_npcs = BooleanField("Spawn NPCs", validators=[Optional()])
    generate_structures = BooleanField("Generate Structures", validators=[Optional()])

    # Final part of the form for naming the server and giving the server a description
    server_name = StringField("Server Name", validators=[InputRequired()])
    server_description = TextAreaField("Description", validators=[Optional()])