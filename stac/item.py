import json
import logging
import os

from string import Formatter, Template
from datetime import datetime

from stac import __version__, STACError, Thing, Collection, utils


logger = logging.getLogger(__name__)


class Item(Thing):

    def __init__(self, *args, **kwargs):
        """ Initialize a scene object """
        super(Item, self).__init__(*args, **kwargs)
        self._assets_by_common_name = None
        self._collection = None

    @property
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
    def eobands(self):
        """ Get eo:bands from Item or from Collection """
        if 'eo:bands' in self.properties:
            return self.properties['eo:bands']
        elif self.collection is not None and 'eo:bands' in self.collection.properties:
                return self.collection['eo:bands']
        return []

    @property
    def properties(self):
        """ Get dictionary of properties """
        return self.data.get('properties', {})

    def __getitem__(self, key):
        """ Get key from properties """
        val = super(Item, self).__getitem__(key)
        if val is None:
            if self.collection is not None:
                # load properties from Collection
                val = self._collection[key]
        return val

    @property
    def date(self):
        dt = self['datetime'].replace('/', '-')
        pattern = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(dt, pattern).date()

    @property
    def geometry(self):
        return self.data['geometry']

    @property
    def bbox(self):
        """ Get bounding box of scene """
        return self.data['bbox']

    @property
    def assets(self):
        """ Return dictionary of assets """
        return self.data.get('assets', {})

    @property
    def assets_by_common_name(self):
        """ Get assets by common band name (only works for assets containing 1 band """
        if self._assets_by_common_name is None and len(self.eobands) > 0:
            self._assets_by_common_name = {}
            for a in self.assets:
                bands = self.assets[a].get('eo:bands', [])
                if len(bands) == 1:
                    eo_band = self.eobands[bands[0]].get('common_name')
                    if eo_band:
                        self._assets_by_common_name[eo_band] = self.assets[a]
        return self._assets_by_common_name

    def asset(self, key):
        """ Get asset for this key OR common_name """
        if key in self.assets:
            return self.assets[key]
        elif key in self.assets_by_common_name:
            return self.assets_by_common_name[key]
        logging.warning('No such asset (%s)' % key)
        return None

    '''
    def string_sub(self, string):
        string = string.replace(':', '_colon_')
        subs = {}
        for key in [i[1] for i in Formatter().parse(string.rstrip('/')) if i[1] is not None]:
            if key == 'date':
                subs[key] = self.datetime
            else:
                subs[key] = self[key.replace('_colon_', ':')]
        return Template(string).substitute(**subs)        

    def get_path(self, no_create=False):
        """ Get local path for this scene """
        path = self.string_sub(config.DATADIR)
        if not no_create and path != '':
            self.mkdirp(path)       
        return path

    def get_filename(self, suffix=None):
        """ Get local filename for this scene """
        fname = self.string_sub(config.FILENAME)
        if suffix is not None:
            fname = fname + suffix
        return fname
    '''

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