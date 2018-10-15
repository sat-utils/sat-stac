import json
import os

import stac
from stac import __version__, utils, Thing


class Catalog(Thing):

    def __init__(self, data, **kwargs):
        """ Initialize a catalog with a catalog file """
        super(Catalog, self).__init__(data, **kwargs)
        self.collections = {}

    @property
    def stac_version(self):
        return self.data['stac_version']

    @property
    def description(self):
        return self.data.get('description', '')

    @classmethod
    def open(cls, filename):
        filename = os.path.join(filename.replace('catalog.json', ''), 'catalog.json')
        return super(Catalog, cls).open(filename)

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
        return cls.open(filename)

    def add_collection(self, collection):
        """ Add a collection to this catalog """
        # add to links
        self.data.links.append({
            'rel': 'collection',
            'href': '%s/catalog.json' % path
            #[self.collections['id']] = collection
        })
        self.save()
