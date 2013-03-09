"""
  flask_ndb_api_csv
  ~~~~~~~~~~~~~~~~~~~

  Flask extension for creating an api with App Engine and ndb.

  :copyright: (c) 2013 by gregorynicholas.
  :license: BSD, see LICENSE for more details.
"""
import csv
from flask import  Response
from codecs import getincrementalencoder
from cStringIO import StringIO
from google.appengine.ext.ndb import blobstore


__all__ = ['is_csv', 'parse_csv_upload', 'send_file_download',
'send_csv_download', 'CsvWriter']


def _unicode(val):
  return unicode(val, 'utf-8', errors='ignore')


def parse_csv_upload(upload, fieldnames):
  # get the blob from the blobstore, read the data out, and immediately
  # delete it..
  blob = blobstore.BlobReader(upload.blob_key)
  csvdata = blob.read().splitlines(True)
  blob_info = blobstore.BlobInfo.get(upload.blob_key)
  if blob_info:
    blob_info.delete()

  # taken from:
  # http://stackoverflow.com/questions/904041/reading-a-utf8-csv-file-with-python
  def _utf8reader(data):
    reader = csv.DictReader(
      data, fieldnames=fieldnames, restval='', dialect='excel')
    reader.next() # offset one row for the header..
    for row in reader:
      yield {key: _unicode(val) for key, val in row.iteritems()}

  return [row for row in _utf8reader(csvdata)]


def is_csv(uploadresult):
  """
    :param uploadresult: Instance of an `flask.ext.gae_blobstore.FieldResult`.
  """
  return uploadresult.name.lower().endswith('.csv')


def send_file_download(data, filename):
  """Sends a file to a client for downloading.

    :param data: Stream data that will be sent as the file contents.
    :param filename: String name of the file.
  """
  headers = {
    'Content-Type': 'text/plain',
    'Content-Disposition': 'attachment; filename={}'.format(filename)}
  return Response(data, headers=headers)


def send_csv_download(fieldnames, row_dicts, filename):
  """
    :param row_dicts: `list` of `dicts`.
  """
  writer = CsvWriter(fieldnames=fieldnames)
  # create a string'ified view of each record..
  writer.writerow({fn: fn for fn in fieldnames})
  [writer.writerow(row) for row in row_dicts]
  # send content disposition..
  return send_file_download(
    data=writer.streamdata(), filename=filename)


class CsvWriter:
  """
  A CSV writer which will write rows to CSV file "f", which is encoded in
  the given encoding.
  """

  def __init__(self, fieldnames, dialect=csv.excel, encoding='utf-8',
      stream=None, **kw):
    if stream is None:
      stream = StringStream()
    self.stream = stream
    # Redirect output to a queue
    self.queue = StringIO()
    self.writer = csv.DictWriter(
      self.queue,
      fieldnames,
      restval='',
      # dialect=dialect,
      extrasaction='ignore')
    self.encoder = getincrementalencoder(encoding)()

  def writerow(self, row_dict):
    def _unicode(val):
      if val and isinstance(val, basestring):
        return val.encode('utf-8')
      return val
    row_dict = {k: _unicode(v) for k, v in row_dict.iteritems()}
    self.writer.writerow(row_dict)
    # Fetch UTF-8 output from the queue..
    data = self.queue.getvalue()
    data = data.decode('utf-8')
    # ...and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream..
    self.stream.write(data)
    # empty queue..
    self.queue.truncate(0)

  def writerows(self, rows):
    [self.writerow(row) for row in rows]

  def streamdata(self):
    """
    Returned the finalized stream output.
    """
    return self.stream.data


class StringStream:
  def __init__(self):
    self.data = ''

  def write(self, value):
    self.data += value
