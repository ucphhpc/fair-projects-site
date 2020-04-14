from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from fair import fair_blueprint, csrf, oid
from projects_base.base.forms import TagsSearchForm
from projects.models import Project
from fair.forms import fairProjectForm, fairProjectSearchForm
from fair.conf import config


@fair_blueprint.route("/")
@fair_blueprint.route("/index", methods=["GET"])
def projects():
    area_choices = fairProjectForm.area.kwargs.get("choices")
    form = TagsSearchForm()
    entities = Project.get_all()
    tags = Project.get_top_with("tags", num=5)
    return render_template(
        "fair/projects.html",
        title=config.get("PROJECTS", "title"),
        grid_header="{}".format(config.get("PROJECTS", "title")),
        tags=list(tags.keys()),
        areas=area_choices,
        objects=entities,
        form=form,
    )


@fair_blueprint.route("/index", methods=["POST"])
def projects_post():
    form = fairProjectSearchForm(request.form)
    if form.validate():
        if form.__contains__("csrf_token"):
            form._fields.pop("csrf_token")
        projects = Project.get_all()
        for key, value in form.data.items():
            if value:
                # Reduce dataset by attribute values
                projects = Project.get_with_attr(key, value, collection=projects)
        entities = [entity.serialize() for entity in projects]
        return jsonify(data={"projects": entities})

    response = jsonify(
        data={
            "danger": ", ".join(
                [msg for attr, errors in form.errors.items() for msg in errors]
            )
        }
    )
    response.status_code = 400
    return response


@fair_blueprint.route("/my_projects", methods=["GET"])
@login_required
def my_projects():
    area_choices = fairProjectForm.area.kwargs.get("choices")
    form = TagsSearchForm()
    entities = [
        project for project in Project.get_all() if project._id in current_user.projects
    ]
    return render_template(
        "fair/projects.html",
        title=config.get("PROJECTS", "title"),
        grid_header="{}".format(config.get("PROJECTS", "title")),
        areas=area_choices,
        objects=entities,
        form=form,
    )


@fair_blueprint.route("/tag/<tag>", methods=["GET"])
def tag_search(tag):
    area_choices = fairProjectForm.area.kwargs.get("choices")
    form = TagsSearchForm(data={"tag": tag}, csrf_enabled=False)
    entities = {}
    tags = Project.get_top_with("tags", num=5)
    if form.validate():
        entities = Project.get_with_search("tags", form.tag.data)

    # Create new form that has csrf -> enable that tag searches can be done
    # via the returned form
    form = TagsSearchForm(data={"tag": tag})
    return render_template(
        "fair/projects.html",
        title=config.get("PROJECTS", "title"),
        grid_header="{}".format(config.get("PROJECTS", "title")),
        tags=list(tags.keys()),
        areas=area_choices,
        objects=entities,
        form=form,
    )


@app.route("/sci_area_search", methods=["POST"])
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
@app.route("/erda_import", methods=["POST"])
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


@app.route("/login", methods=["GET", "POST"])
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
            login_user(user)
            flash("Logged in as the debug user", "success")
            return redirect(url_for("datasets"))
        logged_in = None
        try:
            logged_in = oid.try_login(form.auth_provider.data)
        except Exception as err:
            app.logger.debug("Failed to login {}".format(err))
            return redirect(url_for("login"))
        return logged_in
    return render_template("login.html", form=form, next=oid.get_next_url())


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("datasets"))


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
