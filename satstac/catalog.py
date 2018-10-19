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
        return Catalog(kwargs)

    def children(self):
        """ Get child links """
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

    def add_item(self, item):
        """ Add an item to this catalog """
        if self.filename is None:
            raise STACError('Save catalog before adding items')
        item_link = item.get_filename()
        item_fname = os.path.join(self.path, item_link)
        item_path = os.path.dirname(item_fname)

        cat = self
        dirs = utils.splitall(item_link)
        for d in dirs[:-2]:
            fname = os.path.join(os.path.join(cat.path, d), 'catalog.json')
            # open existing sub-catalog or create new one
            if os.path.exists(fname):
                subcat = Catalog.open(fname)
            else:
                # create a new sub-catalog
                subcat = self.create(id=d).save_as(fname)
                # add the sub-catalog to this catalog
                cat.add_catalog(subcat)
            cat = subcat
            
        # create link to item
        cat.add_link('item', os.path.relpath(item_fname, cat.path))
        cat.save()
    
        # TODO - check if item already exists?
        # create links from item
        item.clean_hierarchy()
        item.add_link('root', os.path.relpath(self.links('root')[0], item_path))
        item.add_link('parent', os.path.relpath(cat.filename, item_path))
        # this assumes the item has been added to a Collection, not a Catalog
        item.add_link('collection', os.path.relpath(self.filename, item_path))

        # save item
        item.save_as(item_fname)
        return self


# import and end of module prevents problems with circular dependencies.
# Catalogs use Items and Items use Collections (which are Catalogs)
from .item import Item
from .collection import Collection