import os
import datetime
from flask import render_template, request, redirect, jsonify, flash, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from requests import get, exceptions
from projects import project_manager
from projects.models import Project, User
from projects.helpers import unique_name_encoding
from fair import fair_blueprint, csrf, oid, app
from fair.forms import LoginForm, ErdaImportForm
from fair.conf import config
from fair.helpers import ErdaHTMLLegacyParser, ErdaHTMLPreTagParser


@fair_blueprint.route("/create_project", methods=["GET", "POST"])
@login_required
def create():
    erda_form = ErdaImportForm()
    form_class = project_manager.get_form_class()
    form = form_class(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():
        f = form.image.data
        # Make sure the saved image is filename is unique
        filename = secure_filename(unique_name_encoding(f.filename))
        f.save(os.path.join(config.get("PROJECTS", "upload_folder"), filename))
        # Remove special fields
        if form.__contains__("csrf_token"):
            form._fields.pop("csrf_token")
        form._fields.pop("image")
        # Save new instance
        new_instance = {
            key: field.data
            for key, field in form.__dict__.items()
            if hasattr(field, "data")
        }

        new_instance["image"] = filename
        entity = Project(**new_instance)
        entity_id = entity.save()
        # Update user with new instance
        current_user.projects.append(entity_id)
        current_user.save()
        url = url_for("projects.show", object_id=entity_id, _external=True)
        flash(
            "Your submission has been received,"
            " your metadata can be found at: " + url,
            "success",
        )
        return redirect(url)
    return render_template(
        "projects/create_project.html", form=form, erda_form=erda_form
    )


# Ajax request upon erda url import
@fair_blueprint.route("/erda_import", methods=["POST"])
@login_required
def erda_import():
    form = ErdaImportForm(request.form)
    if form.validate_on_submit():
        url = form.erda_url.data
        try:
            req = get(url)
        except exceptions.ConnectionError:
            form.errors["connection_error"] = url + " could not be loaded"

        if len(form.errors) < 1 and req.ok:
            tags = ["name", "description", "date"]

            final_parser = None
            parsers = [ErdaHTMLLegacyParser(tags), ErdaHTMLPreTagParser(tags)]
            [parser.feed(req.text) for parser in parsers]
            for parser in parsers:
                if len(parser.result) > 1:
                    final_parser = parser
                    break

            if final_parser is None:
                form.errors["parse_error"] = "No valid fields were found at " + url
            else:
                final_parser.result["date"] = final_parser.result["date"].split()[0]
                return jsonify(data=final_parser.result)

    response = jsonify(data=form.errors)
    response.status_code = 400
    return response


@fair_blueprint.route("/login", methods=["GET", "POST"])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """

    if current_user.is_authenticated:
        flash("Your already logged in", "success")
        return redirect(oid.get_next_url())
    form = LoginForm(request.form)
    if form.validate_on_submit():
        # Debug mode, allow dummy auth
        if app.debug and form.auth_provider.data == "https://openid.ku.dk":
            user = User.get_with_first("openid", app.config["DEBUG_USER"])
            if user:
                login_user(user)
                flash("Logged in as the debug user", "success")
                return redirect(url_for("projects.projects"))
            else:
                flash("No such user could be found", "warning")
                return redirect(url_for("projects.projects"))
        logged_in = None
        try:
            logged_in = oid.try_login(form.auth_provider.data)
        except Exception as err:
            app.logger.debug("Failed to login {}".format(err))
            return redirect(url_for("login"))
        return logged_in
    return render_template("fair/login.html", form=form, next=oid.get_next_url())


@fair_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("projects.projects"))


# Called upon successful login openid auth request
# authenticates the returned identity_url and create a local user if it
# dosen't exist
@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session["openid"] = resp.identity_url
    user = User.get_with_first("openid", resp.identity_url)
    # not a new user
    if user is not None:
        flash("Logged in successfully.", "success")
        login_user(user)
    else:
        # Create new user
        user = User(
            openid=resp.identity_url,
            datasets=[],
            is_active=True,
            is_authenticated=True,
            is_anonymous=False,
            confirmed_on=datetime.datetime.now(),
        )
        user.save()
        login_user(user)
        flash(
            "Success!, Since this is your first login, a local profile was "
            "created for you which is now you active user"
            "for you",
            "success",
        )
    return redirect(oid.get_next_url())
