import os

from .catalog import Catalog
from satstac import STACError, utils


class Collection(Catalog):

    '''
    def __init__(self, *args, **kwargs):
        """ Initialize a scene object """
        super(Collection, self).__init__(*args, **kwargs)
        # determine common_name to asset mapping
        # it will map if an asset contains only a single band
    '''

    @property
    def title(self):
        return self.data.get('title', '')

    @property
    def keywords(self):
        return self.data.get('keywords', [])

    @property
    def version(self):
        return self.data.get('version', '')

    @property
    def license(self):
        return self.data.get('license')

    @property
    def providers(self):
        return self.data.get('providers', [])

    @property
    def extent(self):
        return self.data.get('extent')

    @property
    def properties(self):
        """ Get dictionary of properties """
        return self.data.get('properties', {})

    def add_item(self, item, path='', filename='${id}'):
        """ Add an item to this collection """
        if self.filename is None:
            raise STACError('Save catalog before adding items')
        item_link = item.get_filename(path, filename)
        item_fname = os.path.join(self.path, item_link)
        item_path = os.path.dirname(item_fname)
        root_link = self.links('root')[0]
        root_path = os.path.dirname(root_link)

        cat = self
        dirs = utils.splitall(item_link)
        var_names = [v.strip('$').strip('{}') for v in utils.splitall(path)]
        for i, d in enumerate(dirs[:-2]):
            fname = os.path.join(os.path.join(cat.path, d), 'catalog.json')
            # open existing sub-catalog or create new one
            if os.path.exists(fname):
                subcat = Catalog.open(fname)
            else:
                # create a new sub-catalog
                subcat = self.create(id=d, description='%s catalog' % var_names[i])
                subcat.save_as(fname)
                # add the sub-catalog to this catalog
                cat.add_catalog(subcat)
            cat = subcat
            
        # create link to item
        cat.add_link('item', os.path.relpath(item_fname, cat.path))
        cat.save()

        # create links from item
        item.clean_hierarchy()
        item.add_link('self', os.path.join(self.endpoint(), os.path.relpath(item_fname, root_path)))
        item.add_link('root', os.path.relpath(root_link, item_path))
        item.add_link('parent', os.path.relpath(cat.filename, item_path))
        # this assumes the item has been added to a Collection, not a Catalog
        item.add_link('collection', os.path.relpath(self.filename, item_path))

        # save item
        item.save_as(item_fname)
        return self
