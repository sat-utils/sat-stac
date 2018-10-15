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

    def parent(self):
        """ Get parent link """
        links = self.links('parent')
        if len(links) == 1:
            return Catalog.open(links[0])

    def children(self):
        """ Get child links """
        return [Catalog.open(l) for l in self.links('child')]

    def add_catalog(self, catalog):
        """ Add a catalog to this catalog """
        # add to links
        link = '%s/catalog.json' % catalog.id
        self.data['links'].append({
            'rel': 'child',
            'href': link
        })
        self.save()
        # create catalog
        fname = os.path.abspath(os.path.join(os.path.dirname(self.filename), link))
        catalog.save_as(fname)
