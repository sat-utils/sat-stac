import json
import os

from satstac import __version__, utils, Thing, STACError


class Catalog(Thing):

    def __init__(self, data, **kwargs):
        """ Initialize a catalog with a catalog file """
        super(Catalog, self).__init__(data, **kwargs)

    @property
    def stac_version(self):
        """ Get the STAC version of this catalog """
        return self.data['stac_version']

    @property
    def description(self):
        """ Get catalog description """
        return self.data.get('description', '')

    @classmethod
    def create(cls, id='stac-catalog', description='A STAC Catalog', **kwargs):
        """ Create new catalog """
        kwargs.update({
            'id': id,
            'stac_version': __version__,
            'description': description,
            'links': []
        })
        return cls(kwargs)

    def children(self):
        """ Get child links """
        # TODO = should this be tested if Collection and return mix of Catalogs and Collections?
        return [Catalog.open(l) for l in self.links('child')]

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
            if 'extent' in cat.data.keys():
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

    def add_catalog(self, catalog):
        """ Add a catalog to this catalog """
        if self.filename is None:
            raise STACError('Save catalog before adding sub-catalogs')
        # add new catalog child link
        child_link = '%s/catalog.json' % catalog.id
        child_fname = os.path.join(self.path, child_link)
        child_path = os.path.dirname(child_fname)
        self.add_link('child', child_link)
        self.save()
        # strip self, parent, child links from catalog and add new links
        catalog.clean_hierarchy()
        catalog.add_link('root', os.path.relpath(self.links('root')[0], child_path))
        catalog.add_link('parent', os.path.relpath(self.filename, child_path))
        # create catalog file
        catalog.save_as(child_fname)
        return self

    def publish(self, endpoint):
        """ Update all self links throughout catalog to use new endpoint """
        # we don't use the catalgos and items functions as we'd have to go 
        # through the tree twice, once for catalogs and once for items
        # update myself
        super(Catalog, self).publish(endpoint)
        # update direct items
        for link in self.links('item'):
            item = Item.open(link)
            item.publish(endpoint)
        # follow children
        for cat in self.children():
            cat.publish(endpoint)



# import and end of module prevents problems with circular dependencies.
# Catalogs use Items and Items use Collections (which are Catalogs)
from .item import Item
from .collection import Collection