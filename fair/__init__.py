import os
import datetime
from bcrypt import hashpw, gensalt
from flask import Flask, Blueprint
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_nav import Nav
from projects import base_blueprint, projects_blueprint
from projects.models import User
from projects.helpers import load_user
from projects.nav import nav_bar
from fair.forms import fairProjectForm
from fair.conf import config

app = Flask(__name__)
fair_blueprint = Blueprint(
    "fair",
    __name__,
    static_folder="static",
    static_url_path="/fair/static",
    template_folder="templates",
)
app.register_blueprint(base_blueprint)

csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)

# Setup openid integration
oid = OpenID(
    app,
    safe_roots=[
        "https://fair.erda.dk",
        "http://fair.erda.dk",
        "https://test-ext.idmc.dk",
    ],
    url_root_as_trust_root=True,
)

# Apply styling
Bootstrap(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def fair_load_user(user_id):
    return load_user(user_id)


# Connect mail
mail = Mail(app)

# Setup navbar
nav = Nav()
nav.init_app(app)
nav.register_element("nav_bar", nav_bar)
import fair.views

app.register_blueprint(fair_blueprint)
# Turn of the default endpoint
app.register_blueprint(projects_blueprint)

# Onetime authentication reset token salt
app.config["ONETIME_TOKEN_SALT"] = os.urandom(24)
