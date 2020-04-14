import os
from setuptools import find_packages
from distutils.core import setup

here = os.path.dirname(__file__)
long_description = open("README.rst").read()

version_ns = {}
with open(os.path.join(here, "version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="fair-projects",
    version=version_ns["__version__"],
    long_description=long_description,
    url="https://github.com/ucphhpc/fair-projects-site",
    author="Rasmus Munk",
    author_email="rasmus.munk@nbi.ku.dk",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=["Website", "Flask", "MetaData"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask_wtf", "WTForms", "projects-site"],
)
