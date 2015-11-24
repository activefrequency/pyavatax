#! /usr/bin/env python
from setuptools import setup, find_packages
# python setup.py sdist
# python setup.py sdist bdist_wininst upload

version = __import__('pyavatax').__version__

setup(
    name='PyAvaTax',
    url = 'http://github.com/activefrequency/pyavatax/',
    author = 'John Obelenus',
    author_email = 'jobelenus@activefrequency.com',
    version=version,
    install_requires = ['requests>=2.5.3,<3', 'decorator>=3.4.0', 'six>=1.9.0'],
    package_data = {
        '': ['*.txt', '*.rst', '*.md']
    },
    packages=find_packages(),
    license='BSD',
    long_description="PyAvaTax is a Python library for easily integrating Avalara's RESTful AvaTax API Service",
)
