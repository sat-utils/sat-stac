import json
import os
import stac
from stac.thing import Thing
from stac import utils


class Catalog(object):

    def __init__(self, filename):
        """ Initialize a catalog with a catalog file """
        self.filename = os.path.join(filename.replace('catalog.json', ''), 'catalog.json')
        with open(filename) as f:
            self.cat = json.loads(f.read())
        if 'links' not in self.cat.keys():
            self.cat['links'] = []

    def __getitem__(self, key):
        """ Get key from catalog dictionary """
        if key in ['properties', 'assets']:
            default = {}
        elif key in ['links']:
            default = []
        else:
            default = None
        return self.cat.get(key, default)

    @property
    def id(self):
        return self.cat['id']

    def keys(self):
        """ Get keys from catalog """
        return self.cat.keys()

    @classmethod
    def create(cls, path, catid='stac-catalog', description='A STAC Catalog', **kwargs):
        """ Create new catalog """
        utils.mkdirp(path)
        kwargs.update({
            'id': catid,
            'stac_version': stac.__version__,
            'description': description,
            'links': [
                { 'rel': 'self', 'href': './catalog.json'}
            ]
        })
        filename = os.path.join(path, 'catalog.json')
        with open(filename, 'w') as f:
            f.write(json.dumps(kwargs))
        return cls(filename)

    def save(self):
        """ Update catalog file with current data """
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.cat))

    def add_collection(self, collection):
        """ Add a collection to this catalog """
        col = Catalog(collection)
        self.cat['links'].append({
            'rel': 'collection',
            'href': '%s/catalog.json' % col.id
        })
        self.save()

    @classmethod
    def save_catalog(cls, cat, filename):
        """ Write a catalog file """
        with open(filename, 'w') as f:
            f.write(json.dumps(cat))
