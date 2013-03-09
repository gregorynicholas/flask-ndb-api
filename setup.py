#!/usr/bin/env python
"""
flask-ndb-api
-----------------------

Flask extension for creating an api with App Engine and ndb.

Links
`````

* `documentation <http://packages.python.org/flask-ndb-api>`_
* `development version
  <http://github.com/gregorynicholas/flask-ndb-api/zipball/master#egg=flask-ndb-api-dev>`_

"""
from setuptools import setup

setup(
  name='flask-ndb-api',
  version='1.0.1',
  url='http://github.com/gregorynicholas/flask-ndb-api',
  license='MIT',
  author='gregorynicholas',
  description='Flask extension for creating an api with App Engine and ndb.',
  long_description=__doc__,
  py_modules=['flask_ndb_api', 'flask_ndb_api_forms', 'flask_ndb_api_csv'],
  zip_safe=False,
  platforms='any',
  install_requires=[
    'flask',
    'blinker',
    'Flask-WTF==0.8.2',
    'wtforms-json==0.1.2',
  ],
  tests_require=[
    'nose',
    'flask_gae_tests',
  ],
  dependency_links = [
    'https://github.com/gregorynicholas/flask-gae_tests/tarball/master',
  ],
  test_suite='nose.collector',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
