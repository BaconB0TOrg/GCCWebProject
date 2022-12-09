from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length, Optional, NumberRange

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
    tags = SelectField("Tags", choices=[('SMP', 'SMP')], validators=[Optional()])
    maxPlayers = IntegerField("Maximum Players", validators=[InputRequired(), NumberRange(2, 50)])
    gamemode = SelectField("Gamemode", choices=[('Survival', 'survival'), ('Creative', 'creative')], validators=[InputRequired()])
    # Should not be a field at all. Handled by server based on who is making the server.
    submit = SubmitField("Submit")

class ChangeEmailForm(FlaskForm):
    email = EmailField("New Email", validators=[InputRequired(), Email()])
    submit = SubmitField("Change email")