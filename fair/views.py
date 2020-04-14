from flask import render_template, request, redirect, jsonify, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from projects_base.base.forms import TagsSearchForm
from projects.models import Project, User
from fair import fair_blueprint, csrf, oid, app
from fair.forms import LoginForm
from fair.conf import config


@fair_blueprint.route("/sci_area_search", methods=["POST"])
def sci_area_search():
    form = SciSearchForm(request.form)
    if form.validate_on_submit():
        result = {}
        search_query = request.form["sci_area"]
        areas = DatasetMeta.get_unique_sci_areas()
        area_matches = [
            area
            for area in areas
            if str.find(area, search_query, 0, len(area) - 1) != -1
        ]
        if len(area_matches) > 0:
            result = {"sci_area": area_matches}

        return jsonify(data=result)

    response = jsonify(data={"error": form.errors})
    response.status_code = 400
    return response


# Ajax request upon erda url import
@login_required
@fair_blueprint.route("/erda_import", methods=["POST"])
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


@oid.loginhandler
@fair_blueprint.route("/login", methods=["GET", "POST"])
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


@login_required
@fair_blueprint.route("/logout")
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
