import json
import os
from stac import __version__, utils

class STACError(Exception):
    pass


class Thing(object):

    def __init__(self, data):
        """ Initialize a catalog with a catalog file """
        self.data = data
        if 'links' not in self.data.keys():
            self.data['links'] = []

    @classmethod
    def open(cls, filename):
        """ Open an existing JSON data file """
        with open(filename) as f:
            dat = json.loads(f.read())
        return cls(dat)

    @property
    def id(self):
        return self.data['id']

    def keys(self):
        """ Get keys from catalog """
        return self.data.keys()

    @property
    def links(self):
        return self.data.get('links', [])

    def __getitem__(self, key):
        """ Get key from properties """
        props = self.data.get('properties', {})
        return props.get(key, None)
