# Load environment variables
import argparse
import datetime
from bcrypt import hashpw, gensalt
from fair import app
from projects.models import User

# Handling arguments
parser = argparse.ArgumentParser(description="Start the projects website")
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    default=False,
    help="Whether the application should run in debug mode",
)
parser.add_argument(
    "--ip",
    dest="ip",
    type=str,
    default="127.0.0.1",
    help="The interface the webserver should listen on",
)
parser.add_argument(
    "--port",
    dest="port",
    type=int,
    default=8080,
    help="The port the webserver should listen on",
)
args = parser.parse_args()

if __name__ == "__main__":
    # Implement test user
    if args.debug:
        user = User.get_with_first("email", "test@test.com")
        if user is None:
            user = User(
                email="test@test.com",
                password=hashpw(bytes("test", "utf-8"), gensalt()),
                projects=[],
                is_active=True,
                is_authenticated=True,
                is_anonymous=False,
                confirmed_on=datetime.datetime.now(),
            )
            user.save()
    app.run(host=args.ip, port=args.port, debug=args.debug)
