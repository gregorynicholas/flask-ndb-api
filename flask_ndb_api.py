"""
  flask_ndb_api
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for creating an api with App Engine and ndb.

  :copyright: (c) 2013 by gregorynicholas.
  :license: BSD, see LICENSE for more details.
"""
import logging
from time import mktime
from json import JSONEncoder, loads, dumps
from datetime import date, datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import query


__all__ = ['to_epoch', 'from_epoch', 'NDBJSONEncoder', 'entity_to_dict',
'entity_from_dict', 'entity_from_json', 'ndbpprint', 'ndbdumps']


class NDBJSONEncoder(JSONEncoder):
  """
  `ndb.Model` JSONencoder class.

  Extension of JSONEncoder that can build json from any
  `google.appengine.ext.ndb` object.

  Provides both a specialized simplejson encoder, ModelEncoder, designed to
  simplify encoding directly from NDB Models and query results to json.
  """

  def __init__(self, includes=None, excludes=None, **kw):
    # these two params are eventually passed down from dumps()
    self.__includes = includes
    self.__excludes = excludes
    JSONEncoder.__init__(self, **kw)

  def default(self, obj):
    """
    Returns instance of a `dict` from an ndb object.

      :param value:
        Value to get dictionary for.  If not encodable, will call the
        superclasses default method.
    """
    if isinstance(obj, query.Query):
      return list(obj)

    elif isinstance(obj, ndb.Cursor):
      return obj.urlsafe()

    elif isinstance(obj, ndb.BlobKey):
      return str(obj)

    elif isinstance(obj, ndb.Key):
      return obj.urlsafe()

    elif hasattr(obj, 'to_dict'):
      return getattr(obj, 'to_dict')(
        includes=self.__includes,
        excludes=self.__excludes)

    elif isinstance(obj, datetime):
      return to_epoch(obj)

    elif isinstance(obj, date):
      return to_epoch(datetime(obj.year, obj.month, obj.day))

    return JSONEncoder.default(self, obj)


def to_epoch(value):
  """
  This is a view method to return the data in milli-seconds.

    :param value: Instance of `datetime.datetime`.
    :returns: `float` as the number of seconds since unix epoch.
  """
  return mktime(value.utctimetuple()) * 1000


def from_epoch(value):
  """
    :param value:
      Instance of `float` as the number of seconds since unix epoch.
    :returns:
      Instance of `datetime.datetime`.
  """
  return datetime.utcfromtimestamp(value / 1000)


def entity_to_dict(self, includes=None, excludes=None):
  """
  Encodes an `ndb.Model` to a `dict`. By default, only `ndb.Property`
  attributes are included in the result.

    :param include:
      List of strings keys of class attributes. Can be the name of the
      either a method or property.
    :param exclude:
      List of string keys to omit from the return value.
    :returns: Instance of `dict`.
    :raises: `ValueError` if any key in the `include` param doesn't exist.
  """
  self._fix_up_properties() # without this we're fucked..
  value = ndb.Model.to_dict(self)
  # set the `id` of the entity's key by default..
  if self.key and (not excludes or 'key' not in excludes):
    value['key'] = self.key.urlsafe()
    value['key_id'] = self.key.id()

  def _to_dict(value):
    if callable(value):
      return value()
    elif isinstance(value, ndb.Model):
      return entity_to_dict(value, includes=includes, excludes=excludes)
    elif isinstance(value, list):
      return [_to_dict(v) for v in value]
    else:
      return value

  if includes:
    for inc in includes:
      attr = self._properties.get(inc)
      if attr is not None:
        value[inc] = attr._get_value(self)
        continue
      logging.warn('entity_to_dict cannot encode `%s`. Property is '
        'not defined on `%s.%s`.',
        inc, self.__class__.__module__, self.__class__.__name__)

      attr = getattr(self, inc, None)
      if attr is None:
        logging.warn('entity_to_dict cannot encode `%s`. Attribute is '
          'not defined on `%s.%s`.',
          inc, self.__class__.__module__, self.__class__.__name__)
        continue

      value[inc] = _to_dict(attr)
  if excludes:
    # exclude items from the result dict, by popping the keys
    # from the dict..
    (value.pop(exc) for exc in excludes if exc in value)
  return value


def entity_from_dict(cls, value):
    """
      :param cls: `ndb.Model` subclass.
      :param value: Instance of a `dict`.
    """
    entity = cls()
    entity._fix_up_properties() # without this we're fucked..

    def _decode(_key, _value):
      """
      Deserializes `dict`s values to `ndb.Property` values.
      """
      prop = entity._properties.get(_key)
      if prop is None:
        logging.warn('entity_from_dict cannot decode: `%s`. Property is \
not defined on: `%s.%s`.', _key, cls.__module__, cls.__name__)
        continue

      if isinstance(prop, (ndb.DateTimeProperty, ndb.DateProperty,
                           ndb.TimeProperty)):
        if prop._repeated:
          val = [from_epoch(v) for v in _value if v is not None]
        elif val:
          val = from_epoch(val)
      if isinstance(prop, ndb.BlobKeyProperty):
        if prop._repeated:
          val = [ndb.BlobKey(str(v)) for v in _value if v is not None]
        elif val:
          val = ndb.BlobKey(str(val))
      if isinstance(prop, ndb.KeyProperty):
        if prop._repeated:
          val = [ndb.Key(urlsafe=v) for v in _value if v is not None]
        elif val:
          val = ndb.Key(urlsafe=val)
      if isinstance(prop, ndb.BlobProperty):
        # not supported..
        pass
      return val

    values = {k: _decode(k, v) for k, v in value.iteritems()}
    entity.populate(**values)
    return entity


def entity_from_json(cls, value):
  """
  Deserializes a json str to an instance of an `ndb.Model` subclass.

    :param cls: `ndb.Model` subclass.
    :param value: Instance of json data.
  """
  value = loads(value, strict=False)
  if isinstance(value, list):
    result = [entity_from_dict(cls, v) for v in value]
  else:
    result = entity_from_dict(cls, value)
  return result


def ndbdumps(value, includes=None, excludes=None):
  """
    :param value:
    :param include:
      List of string keys of class attributes. Can be the name of the
      either a callable method or property.
    :param exclude:
      List of string keys to omit from the return value.
    :returns: JSON string.
  """
  return dumps(value,
    cls=NDBJSONEncoder, includes=includes, excludes=excludes)


def ndbpprint(model, level=1):
  """
  Pretty prints an `ndb.Model`.
  """
  body = ['<', type(model).__name__, ':']
  values = model.to_dict()
  for key, field in model._properties.iteritems():
    value = values.get(key)
    if value is not None:
      body.append('\n%s%s: %s' % (
      ' '.join([' ' for idx in range(level)]), key, repr(value)))
  body.append('>')
  return ''.join(body)


def key_or_none(value):
  """
  Attempts to parse a value into an instance of an `ndb.Key`.

    :returns: None if value cannot be converted to an `ndb.Key`.
  """
  if not value:
    return None
  if isinstance(value, str) and len(value) < 1:
    return None
  return ndb.Key(urlsafe=value)
