import os
import logging
import json
from string import Formatter, Template
from datetime import datetime
import stac.utils as utils
import traceback


logger = logging.getLogger(__name__)


class ItemError(Exception):
    pass


class Item(object):

    def __init__(self, feature):
        """ Initialize a scene object """
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

    def __repr__(self):
        return self.id

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except:
            if key in self.feature['properties']:
                return self.feature['properties'][key]
            else:
                return None

    @property
    def id(self):
        return self.feature['id']

    @property
    def datetime(self):
        dt = self['datetime'].replace('/', '-')
        pattern = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(dt, pattern).date()

    @property
    def properties(self):
        return self.feature['properties'].keys()

    @property
    def geometry(self):
        return self.feature['geometry']

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

    @property
    def links(self):
        """ Return dictionary of links """
        return self.feature.get('links', {})

    @property
    def eobands(self):
        """ Return dictionary of eo:bands """
        return self.feature['properties'].get('eo:bands', {})

    def asset(self, key):
        """ Get asset info for this key OR common_name """
        if key not in self.assets:
            if key not in self.name_to_band:
                logging.warning('No such asset (%s)' % key)
                return None
            else:
                key = self.name_to_band[key]
        return self.assets[key]

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


class Items(object):
    """ A collection of Scene objects """

    def __init__(self, scenes, properties={}):
        """ Initialize with a list of Scene objects """
        self.scenes = sorted(scenes, key=lambda s: s.date)
        self.properties = properties
        for p in properties:
            if isinstance(properties[p], str):
                try:
                    _p = json.loads(properties[p])
                    self.properties[p] = _p
                except:
                    self.properties[p] = properties[p]
            # check if FeatureCollection and get just first Feature
            if p == 'intersects':
                if self.properties[p]['type'] == 'FeatureCollection':
                    self.properties[p] = self.properties[p]['features'][0]
        self.collections

    def __len__(self):
        """ Number of scenes """
        return len(self.scenes)

    def __getitem__(self, index):
        return self.scenes[index]

    def __setitem__(self, index, value):
        self.scenes[index] = value

    def __delitem__(self, index):
        self.scenes.delete(index)

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted(list(set([s.date for s in self.scenes])))

    def collections(self):
        """ Get collection records for this list of scenes """
        return self.collections

    def bbox(self):
        """ Get bounding box of search """
        if 'intersects' in self.properties:
            coords = self.properties['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [min(lons), min(lats), max(lons), max(lats)]
        else:
            return []

    def center(self):
        if 'intersects' in self.properties:
            coords = self.properties['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [(min(lats) + max(lats))/2.0, (min(lons) + max(lons))/2.0]
        else:
            return 0, 0

    def platforms(self, date=None):
        """ List of all available sensors across scenes """
        if date is None:
            return list(set([s['eo:platform'] for s in self.scenes]))
        else:
            return list(set([s['eo:platform'] for s in self.scenes if s.date == date]))

    def print_scenes(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'id']
        txt = 'Scenes (%s):\n' % len(self.scenes)
        txt += ''.join(['{:<20}'.format(p) for p in params]) + '\n'
        for s in self.scenes:
            # NOTE - the string conversion is because .date returns a datetime obj
            txt += ''.join(['{:<20}'.format(str(s[p])) for p in params]) + '\n'
        print(txt)

    def text_calendar(self):
        """ Get calendar for dates """
        date_labels = {}
        dates = self.dates()
        if len(dates) == 0:
            return ''
        for d in self.dates():
            sensors = self.platforms(d)
            if len(sensors) > 1:
                date_labels[d] = 'Multiple'
            else:
                date_labels[d] = sensors[0]
        return utils.get_text_calendar(date_labels)

    def save(self, filename):
        """ Save scene metadata """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.geojson()))

    def geojson(self):
        """ Get all metadata as GeoJSON """
        features = [s.feature for s in self.scenes]
        return {
            'type': 'FeatureCollection',
            'features': features,
            'properties': self.properties
        }

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a GeoJSON file of metadata """
        with open(filename) as f:
            geoj = json.loads(f.read())
        scenes = [Scene(feature) for feature in geoj['features']]
        return Scenes(scenes, properties=geoj.get('properties', {}))

    def filter(self, key, values):
        """ Filter scenes on key matching value """
        scenes = []
        for val in values:
            scenes += list(filter(lambda x: x[key] == val, self.scenes))
        self.scenes = scenes

    def download(self, **kwargs):
        dls = []
        for s in self.scenes:
            fname = s.download(**kwargs)
            if fname is not None:
                dls.append(fname)
        return dls
