import logging
import functools
import os

from datetime import datetime

from .catalog import Catalog
from satstac import STACError, utils

logger = logging.getLogger(__name__)


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
        return self._data.get('title', '')

    @property
    def keywords(self):
        return self._data.get('keywords', [])

    @property
    def version(self):
        return self._data.get('version', '')

    @property
    def license(self):
        return self._data.get('license')

    @property
    def providers(self):
        return self._data.get('providers', [])

    @property
    def extent(self):
        return self._data.get('extent')

    @property
    def summaries(self):
        """ Get dictionary of summaries """
        return self._data.get('summaries', {})

    @functools.lru_cache()
    def parent_catalog(self, item, path_template):
        """ Given relative filename to a new Item find parent catalog """
        cat = self
        path = item.get_path(os.path.dirname(path_template))
        var_names = [v.strip('$').strip('{}') for v in utils.splitall(path_template)]
        for i, d in enumerate(utils.splitall(path)):
            fname = os.path.join(os.path.join(cat.path, d), 'catalog.json')
            # open existing sub-catalog or create new one
            try:
                subcat = Catalog.open(fname)
            except STACError as err:
                # create a new sub-catalog
                subcat = self.create(id=d, description='%s catalog' % var_names[i])
                subcat.save(filename=fname)
                # add the sub-catalog to this catalog
                cat.add_catalog(subcat)
            cat = subcat
        return cat.filename

    def add_item(self, item, filename_template='${id}.json'):
        """ Add an item to this collection """
        start = datetime.now()
        if self.filename is None:
            raise STACError('Save catalog before adding items')
        item_link = os.path.join(item.get_path(os.path.join(filename_template)))
        item_fname = os.path.join(self.path, item_link)
        item_path = os.path.dirname(item_fname)
        root_link = self.links('root')[0]
        #root_path = os.path.dirname(root_link)
        parent = Catalog.open(self.parent_catalog(item, filename_template))
        
        # create link to item
        parent.add_link('item', os.path.relpath(item_fname, parent.path))
        parent.save()

        # create links from item
        item.clean_hierarchy()
        item.add_link('root', os.path.relpath(root_link, item_path))
        item.add_link('parent', os.path.relpath(parent.filename, item_path))
        # this assumes the item has been added to a Collection, not a Catalog
        item.add_link('collection', os.path.relpath(self.filename, item_path))

        # save item
        
        item.save(filename=item_fname)
        logger.debug('Added %s in %s seconds' % (item.filename, datetime.now()-start))
        
        return self
