import json
import logging
import os
import traceback

from string import Formatter, Template
from datetime import datetime
from dateutil.parser import parse as dateparse

from satstac import __version__, STACError, Thing, utils

logger = logging.getLogger(__name__)

FILENAME_TEMPLATE = os.getenv('SATSEARCH_FILENAME_TEMPLATE', '${collection}/${date}/${id}')


class Item(Thing):

    def __init__(self, *args, **kwargs):
        """ Initialize a scene object """
        super(Item, self).__init__(*args, **kwargs)
        # dictionary of assets by eo:band common_name
        self._assets_by_common_name = None
        # collection instance
        self._collection = kwargs.pop('collection', None)
        # TODO = allow passing in of collection (needed for FC catalogs)

    def collection(self):
        """ Get Collection info for this item """
        if self._collection is None:
            if self.filename is None:
                # TODO - raise exception ?
                return None
            link = self.links('collection')
            if len(link) == 1:
                self._collection = Collection.open(link[0])
        return self._collection

    @property
    def properties(self):
        """ Get dictionary of properties """
        return self._data.get('properties', {})

    def __getitem__(self, key):
        """ Get key from properties """
        val = super(Item, self).__getitem__(key)
        if val is None:
            if self.collection() is not None:
                # load properties from Collection
                val = self._collection[key]
        return val

    @property
    def date(self):
        return self.datetime.date()

    @property
    def datetime(self):
        return dateparse(self['datetime'])

    @property
    def geometry(self):
        return self._data['geometry']

    @property
    def bbox(self):
        """ Get bounding box of scene """
        return self._data['bbox']

    @property
    def assets(self):
        """ Return dictionary of assets """
        return self._data.get('assets', {})

    @property
    def assets_by_common_name(self):
        """ Get assets by common band name (only works for assets containing 1 band """
        if self._assets_by_common_name is None:
            self._assets_by_common_name = {}
            for a in self.assets:
                bands = []
                col = self.collection()._data
                if 'eo:bands' in self.assets[a]:
                    bands = self.assets[a]['eo:bands']
                elif 'item_assets' in col:
                    bands = col['item_assets'][a].get('eo:bands', [])
                if len(bands) == 1:
                    eo_band = bands[0].get('common_name')
                    if eo_band:
                        self._assets_by_common_name[eo_band] = self.assets[a]
        return self._assets_by_common_name

    def asset(self, key):
        """ Get asset for this key OR common_name """
        if key in self.assets.keys():
            return self.assets[key]
        elif key in self.assets_by_common_name:
            return self.assets_by_common_name[key]
        logging.warning('No such asset (%s)' % key)
        return None

    def get_path(self, template):
        """ Substitute envvars in template with Item values """
        _template = template.replace(':', '__colon__')
        subs = {}
        for key in [i[1] for i in Formatter().parse(_template.rstrip('/')) if i[1] is not None]:
            if key == 'collection':
                # make this compatible with older versions of stac where collection is in properties
                subs[key] = self._data.get('collection', self['collection'])
            elif key == 'id':
                subs[key] = self.id
            elif key in ['date', 'year', 'month', 'day']:
                vals = {'date': self.date, 'year': self.date.year, 'month': self.date.month, 'day': self.date.day}
                subs[key] = vals[key]
            else:
                subs[key] = self[key.replace('__colon__', ':')]
        return Template(_template).substitute(**subs).replace('__colon__', ':')

    def download_assets(self, keys=None, **kwargs):
        """ Download multiple assets """
        if keys is None:
            keys = self._data['assets'].keys()
        filenames = []
        for key in keys:
            filenames.append(self.download(key, **kwargs))
        return filenames

    def download(self, key, overwrite=False, filename_template=FILENAME_TEMPLATE, requester_pays=False, headers={}):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        asset = self.asset(key)
        if asset is None:
            return None

        ext = os.path.splitext(asset['href'])[1]
        filename = self.get_path(filename_template) + '_' + key + ext
        if not os.path.exists(filename) or overwrite:
            try:
                utils.download_file(asset['href'], filename=filename, requester_pays=requester_pays, headers=headers)
            except Exception as e:
                filename = None
                logger.error('Unable to download %s: %s' % (asset['href'], str(e)))
                logger.debug(traceback.format_exc())
        return filename

    '''
    @classmethod
    def create_derived(cls, scenes):
        """ Create metadata for dervied scene from multiple input scenes """
        # data provenance, iterate through links
        links = []
        for i, scene in enumerate(scenes):
            links.append({
                'rel': 'derived_from',
                'href': scene.links['self']['href']
            })
        # calculate composite geometry and bbox
        geom = scenes[0].geometry
        # properties
        props = {
            'id': '%s_%s' % (scenes[0].date, scenes[0]['eo:platform']),
            'datetime': scenes[0]['datetime']
        }
        collections = [s['c:id'] for s in scenes if s['c:id'] is not None]
        if len(collections) == 1:
            props['c:id'] = collections[0]
        item = {
            'properties': props,
            'geometry': geom,
            'links': links,
            'assets': {}
        }
        return Item(item)
    '''

# import and end of module prevents problems with circular dependencies.
# Catalogs use Items and Items use Collections (which are Catalogs)
from .collection import Collection
