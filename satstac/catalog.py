import json
import os

from .version import __version__
from .thing import Thing, STACError

STAC_VERSION = os.getenv('STAC_VERSION', '1.0.0-beta.2')


class Catalog(Thing):

    def __init__(self, data, root=None, **kwargs):
        """ Initialize a catalog with a catalog file """
        super(Catalog, self).__init__(data, **kwargs)

    @property
    def stac_version(self):
        """ Get the STAC version of this catalog """
        return self._data['stac_version']

    @property
    def description(self):
        """ Get catalog description """
        return self._data.get('description', '')

    @classmethod
    def create(cls, id='stac-catalog', title='A STAC Catalog', 
               description='A STAC Catalog', root=None, **kwargs):
        """ Create new catalog """
        kwargs.update({
            'id': id,
            'stac_version': STAC_VERSION,
            'title': title,
            'description': description,
            'links': []
        })
        return cls(kwargs, root=root)

    def children(self):
        """ Get child links """
        # TODO = should this be tested if Collection and return mix of Catalogs and Collections?
        for l in self.links('child'):
            yield Catalog.open(l)

    def catalogs(self):
        """ Recursive get all catalogs within this Catalog """
        for cat in self.children():
            for subcat in cat.children():
                yield subcat
                yield from subcat.catalogs()
            yield cat

    def collections(self):
        """ Recursively get all collections within this Catalog """
        for cat in self.children():
            if 'extent' in cat._data.keys():
                yield Collection.open(cat.filename)
                # TODO - keep going? if other Collections can appear below a Collection
            else:
                yield from cat.collections()

    def items(self):
        """ Recursively get all items within this Catalog """
        for item in self.links('item'):
            yield Item.open(item)
        for child in self.children():
            yield from child.items()

    def add_catalog(self, catalog, basename='catalog'):
        """ Add a catalog to this catalog """
        if self.filename is None:
            raise STACError('Save catalog before adding sub-catalogs')
        # add new catalog child link
        child_link = '%s/%s.json' % (catalog.id, basename)
        child_fname = os.path.join(self.path, child_link)
        child_path = os.path.dirname(child_fname)
        root_links = self.links('root')
        root_link = root_links[0] if len(root_links) > 0 else self.filename
        root_path = os.path.dirname(root_link)
        self.add_link('child', child_link)
        self.save()
        # strip self, parent, child links from catalog and add new links
        catalog.clean_hierarchy()
        catalog.add_link('root', os.path.relpath(root_link, child_path))
        catalog.add_link('parent', os.path.relpath(self.filename, child_path))
        # create catalog file
        catalog.save(filename=child_fname)
        return self

    def add_collection(self, catalog, basename='collection'):
        """ Add a collection to this catalog """
        return self.add_catalog(catalog, basename=basename)


# import and end of module prevents problems with circular dependencies.
# Catalogs use Items and Items use Collections (which are Catalogs)
from .item import Item
from .collection import Collection
