import json
import os.path as op
import requests

from logging import getLogger
from .catalog import STAC_VERSION
from .collection import Collection
from .item import Item
from .thing import STACError
from .utils import terminal_calendar, get_s3_signed_url

logger = getLogger(__name__)


class ItemCollection(object):
    """ A GeoJSON FeatureCollection of STAC Items with associated Collections """

    def __init__(self, items, collections=[]):
        """ Initialize with a list of Item objects """
        self._collections = collections
        self._items = items
        # link Items to their Collections
        cols = {c.id: c for c in self._collections}
        for i in self._items:
            # backwards compatible to STAC 0.6.0 where collection is in properties
            col = i._data.get('collection', None)
            if col is not None:
                if col in cols:
                    i._collection = cols[col]

    @classmethod
    def open_remote(self, url, headers={}):
        """ Open remote file """
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            dat = resp.text
        else:
            raise STACError('Unable to open %s' % url)
        return json.loads(dat)

    @classmethod
    def open(cls, filename):
        """ Load an Items class from a GeoJSON FeatureCollection """
        """ Open an existing JSON data file """
        logger.debug('Opening %s' % filename)
        if filename[0:5] == 'https':
            try:
                data = cls.open_remote(filename)
            except STACError as err:
                # try signed URL
                url, headers = get_s3_signed_url(filename)
                data = cls.open_remote(url, headers)
        else:
            if op.exists(filename):
                data = open(filename).read()
                data = json.loads(data)
            else:
                raise STACError('%s does not exist locally' % filename)
        collections = [Collection(col) for col in data.get('collections', [])]
        items = [Item(feature) for feature in data['features']]
        return cls(items, collections=collections)

    @classmethod
    def load(cls, *args, **kwargs):
        """ Load an Items class from a GeoJSON FeatureCollection """
        logger.warning("ItemCollection.load() is deprecated, use ItemCollection.open()")
        return cls.open(*args, **kwargs)

    def __len__(self):
        """ Number of scenes """
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted(list(set([s.date for s in self._items])))

    def collection(self, id):
        """ Get collection records for this list of scenes """
        cols = [c for c in self._collections if c.id == id]
        if len(cols) == 1:
            return cols[0]
        else:
            return None

    def properties(self, key, date=None):
        """ Set of values for 'key' property in Items, for specific date if provided """
        if date is None:
            return list(set([i[key] for i in self._items]))
        else:
            return list(set([i[key] for i in self._items if i.date == date]))    

    def summary(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'id']
        txt = 'Items (%s):\n' % len(self._items)
        txt += ''.join(['{:<25} '.format(p) for p in params]) + '\n'
        for s in self._items:
            txt += ''.join(['{:<25} '.format(s.get_path('${%s}' % p)) for p in params]) + '\n'
        return txt

    def calendar(self, group='platform'):
        """ Get calendar for dates """
        date_labels = {}
        for d in self.dates():
            groups = self.properties(group, d)
            if len(groups) > 1:
                date_labels[d] = 'Multiple'
            else:
                date_labels[d] = groups[0]
        return terminal_calendar(date_labels)

    def assets_definition(self):
        fields = ['Key', 'Title', 'Common Name(s)', 'Type']
        w = [12, 35, 20, 50]
        for c in self._collections:
            txt = f"Collection: {c.id}\n"
            txt += ''.join([f"{fields[i]:{w[i]}}" for i in range(len(w))]) + '\n'
            for key in c._data['item_assets']:
                asset = c._data['item_assets'][key]
                if 'eo:bands' in asset:
                    bands = ', '.join([b.get('common_name', None) for b in asset['eo:bands'] if 'common_name' in b])
                else:
                    bands = ''
                #import pdb; pdb.set_trace()
                vals = [key, asset['title'], bands, asset['type']]
                txt += ''.join([f"{vals[i]:{w[i]}}" for i in range(len(w))]) + '\n'
        return txt

    def save(self, filename, **kwargs):
        """ Save scene metadata """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.geojson(**kwargs)))

    def geojson(self, id='STAC', description='Single file STAC'):
        """ Get Items as GeoJSON FeatureCollection """
        features = [s._data for s in self._items]
        geoj = {
            'id': id,
            'description': description,
            'stac_version': STAC_VERSION,
            'stac_extensions': ['single-file-stac'],
            'type': 'FeatureCollection',
            'features': features,
            'collections': [c._data for c in self._collections],
            'links': []
        }
        return geoj

    def filter(self, key, values):
        """ Filter scenes on key matching value """
        items = []
        for val in values:
            items += list(filter(lambda x: x[key] == val, self._items))
        self._items = items

    def download_assets(self, *args, **kwargs):
        filenames = []
        for i in self._items:
            fnames = i.download_assets(*args, **kwargs)
            if len(fnames) > 0:
                filenames.append(fnames)
        return filenames

    def download(self, *args, **kwargs):
        """ Download all Items """
        dls = []
        for i in self._items:
            fname = i.download(*args, **kwargs)
            if fname is not None:
                dls.append(fname)
        return dls
