import os
from projects.conf import config

config.read(os.path.abspath(os.path.join("res", "config.ini")))
