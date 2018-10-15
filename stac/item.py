import json
import logging
import os

from string import Formatter, Template
from datetime import datetime

from stac import __version__, Thing, utils


logger = logging.getLogger(__name__)


class Item(Thing):

    def __init__(self, *args, **kwargs):
        """ Initialize a scene object """
        super(Item, self).__init__(*args, **kwargs)
        '''
        # skip validation for now, use other library if available
        required = ['id', 'datetime']
        if 'geometry' not in feature:
            raise ItemError('No geometry supplied')
        if 'properties' not in feature:
            raise ItemError('No properties supplied')
        if not set(required).issubset(feature.get('properties', {}).keys()):
            raise ItemError('Invalid Scene (required parameters: %s' % ' '.join(required))
        '''
        self.feature = feature

        '''
        # determine common_name to asset mapping
        # it will map if an asset contains only a single band
        bands = self.eobands
        band_to_name = {b: bands[b]['common_name'] for b in bands if bands[b].get('common_name', None)}
        self.name_to_band = {}
        for a in self.assets:
            _bands = self.assets[a].get('eo:bands', [])
            if len(_bands) == 1 and _bands[0] in band_to_name:
                self.name_to_band[band_to_name[_bands[0]]] = _bands[0]

        self.filenames = {}
        '''
        '''
        bands = self.eobands
        band_to_name = {b: bands[b]['common_name'] for b in bands if bands[b].get('common_name', None)}
        self.name_to_band = {}
        for a in self.assets:
            _bands = self.assets[a].get('eo:bands', [])
            if len(_bands) == 1 and _bands[0] in band_to_name:
                self.name_to_band[band_to_name[_bands[0]]] = _bands[0]
        '''

    @property
    def datetime(self):
        dt = self['datetime'].replace('/', '-')
        pattern = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(dt, pattern).date()

    @property
    def geometry(self):
        return self.data['geometry']

    @property
    def bbox(self):
        """ Get bounding box of scene """
        lats = [c[1] for c in self.geometry['coordinates'][0]]
        lons = [c[0] for c in self.geometry['coordinates'][0]]
        return [min(lons), min(lats), max(lons), max(lats)]

    @property
    def assets(self):
        """ Return dictionary of assets """
        return self.feature.get('assets', {})

    def asset(self, key):
        """ Get asset info for this key OR common_name """
        if key not in self.assets:
            if key not in self.name_to_band:
                logging.warning('No such asset (%s)' % key)
                return None
            else:
                key = self.name_to_band[key]
        return self.assets[key]

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