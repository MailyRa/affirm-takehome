# coding: utf-8
import os

from setuptools import setup

NAME = "loan_application"
VERSION = "1.0.0"

here = os.path.abspath(os.path.dirname(__file__))


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


def read_file(file_name):
    file_path = os.path.join(here, file_name)
    return open(file_path, encoding='utf-8').read().strip()


def parse_requirements(file_name):
    with open(os.path.join(here, file_name), encoding='utf-8') as f:
        return [x for x in f if len(x) > 0 and x[0] not in ('-', '#')]


setup(
    name=NAME,
    version=VERSION,
    description="Loan Application Lite",
    author_email="",
    url="",
    keywords=["OpenAPI", "Loan Application Lite"],
    install_requires=parse_requirements("requirements.txt"),
    packages=['loan_application'],
    package_data={'': ['loan_application/app/openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['loan_application_server=loan_application.app.__main__:main']},
    long_description="""\
    """  # noqa: E501
)
