from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, HiddenField, TextAreaField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Email, Length, Optional, NumberRange
from flask import request, url_for, redirect
from urllib.parse import urlparse, urljoin


# from https://web.archive.org/web/20120501162055/http://flask.pocoo.org/snippets/63/
def is_safe_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, str(target)))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
    target = request.args.get('next')
    if is_safe_url(target):
        return target
    return None

class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='welcome', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

class LoginForm(RedirectForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RegisterForm(RedirectForm):
    username = StringField("Username", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    confirm_email = EmailField("Confirm Email", validators=[InputRequired(
    ), Email(), EqualTo('email', message="Email addresses Do Not Match.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(
        min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField("Confirm Password", validators=[
                                     InputRequired(), EqualTo('password', message="Passwords Do Not Match.")])
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
    tags = SelectMultipleField("Tags", validators=[Optional()], coerce=int)
    maxPlayers = IntegerField("Maximum Players", validators=[
                              InputRequired(), NumberRange(2, 50)])
    gamemode = SelectField("Gamemode", choices=[(
        'survival', 'Survival'), ('creative', 'Creative')], validators=[InputRequired()])
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
