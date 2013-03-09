"""
  flask_ndb_api_forms
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for creating an api with App Engine and ndb.

  :copyright: (c) 2013 by gregorynicholas.
  :license: BSD, see LICENSE for more details.
"""
import logging
from flask import request
from flask.exceptions import JSONBadRequest
from functools import wraps
from json import loads
from pprint import pformat
from wtforms import StringField
from google.appengine.ext import ndb


__all__ = ['formed', 'KeyField', 'BlobKeyField', 'CursorField']


def formed(form):
  def _formed(fn):
    @wraps(fn)
    def wrapped(*args, **kw):
      if request.json or 'json' in request.form:
        if request.json:
          json = request.json.get('params')
        else:
          json = loads(request.form['json'])
        if not json:
          raise JSONBadRequest()
        _form = form.from_json(json)
      else:
        _form = form(request.form)
      result = _form.validate_on_submit()
      if not result:
        for k, v in _form.errors.iteritems():
          _form.errors[k] = ''.join(v)
        logging.warning('Error validating json data: %s, %s',
          pformat(_form.errors), type(_form.errors))
        raise ValueError('Validation error occurred: %s' % _form.errors)
      return fn(form=_form, *args, **kw)
    return wrapped
  return _formed


class KeyField(StringField):

  def __init__(self, kind=None, *args, **kwds):
    self.kind = kind
    StringField.__init__(self, *args, **kwds)

  def process_data(self, value):
    try:
      self.data = ndb.Key(urlsafe=value)
    except ValueError:
      self.data = None
      raise ValueError(self.gettext('Not a valid ndb.Key value'))
    if self.data.kind() is not self.kind:
      raise ValueError(self.gettext('Not a valid ndb.Key kind'))

  def __call__(self, **kwargs):
    return self.data.urlsafe()


class BlobKeyField(StringField):
  pass # todo


class CursorField(StringField):

  def __call__(self, **kwargs):
    return self.data.urlsafe()

