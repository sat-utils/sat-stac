import json
import logging
import os
import traceback

from string import Formatter, Template
from datetime import datetime
from dateutil.parser import parse as dateparse

from satstac import __version__, STACError, Thing, utils


logger = logging.getLogger(__name__)


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
    def eobands(self):
        """ Get eo:bands from Item or from Collection """
        if 'eo:bands' in self.properties:
            return self.properties['eo:bands']
        elif self.collection() is not None and 'eo:bands' in self.collection().properties:
                return self.collection()['eo:bands']
        return []

    @property
    def properties(self):
        """ Get dictionary of properties """
        return self.data.get('properties', {})

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

    def get_filename(self, path='', filename='${id}', extension='.json'):
        """ Get complete path with filename to this item """
        return os.path.join(
            self.substitute(path),
            self.substitute(filename) + extension
        )

    def substitute(self, string):
        """ Substitute envvars in string with Item values """
        string = string.replace(':', '_colon_')
        subs = {}
        for key in [i[1] for i in Formatter().parse(string.rstrip('/')) if i[1] is not None]:
            if key == 'id':
                subs[key] = self.id
            elif key in ['date', 'year', 'month', 'day']:
                vals = {'date': self.date, 'year': self.date.year, 'month': self.date.month, 'day': self.date.day}
                subs[key] = vals[key]
            else:
                subs[key] = self[key.replace('_colon_', ':')]
        return Template(string).substitute(**subs)   

    def download_assets(self, keys=None, **kwargs):
        """ Download multiple assets """
        if keys is None:
            keys = self.data['assets'].keys()
        filenames = []
        for key in keys:
            filenames.append(self.download(key, **kwargs))
        return filenames

    def download(self, key, overwrite=False, path='', filename='${id}', requestor_pays=False):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        asset = self.asset(key)
        if asset is None:
            return None

        _path = self.substitute(path)
        utils.mkdirp(_path)
        _filename = None
        try:
            fname = self.substitute(filename)
            ext = os.path.splitext(asset['href'])[1]
            fout = os.path.join(_path, fname + '_' + key + ext)
            if not os.path.exists(fout) or overwrite:
                _filename = utils.download_file(asset['href'], filename=fout, requestor_pays=requestor_pays)
            else:
                _filename = fout
        except Exception as e:
            _filename = None
            logger.error('Unable to download %s: %s' % (asset['href'], str(e)))
            logger.debug(traceback.format_exc())
        return _filename

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