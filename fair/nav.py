from flask_login import current_user
from flask_nav.elements import Navbar, View
from projects.conf import config
from fair import nav


@nav.navigation()
def nav_bar():
    navbar = list(
        Navbar(
            View("{}".format(config.get("PROJECTS", "title")), "projects.projects"),
            View("Datasets", "projects.projects"),
        ).items
    )
    if current_user.is_authenticated:
        navbar.extend(
            [
                View("My Datasets", "projects.my_projects"),
                View("Create Dataset", "projects.create"),
                View("Logout", "projects.logout"),
            ]
        )
    else:
        navbar.extend(
            [View("Login", "projects.login"),]
        )

    return Navbar("{}".format(config.get("PROJECTS", "title")), *navbar)
