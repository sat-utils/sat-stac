import json

from .collection import Collection
from .item import Item
from .utils import terminal_calendar


class Items(object):
    """ A GeoJSON FeatureCollection of STAC Items with associated Collections """

    def __init__(self, items, collections=[], search={}):
        """ Initialize with a list of Item objects """
        self._collections = collections
        self._items = items
        self._search = search
        # link Items to their Collections
        cols = {c.id: c for c in self._collections}
        for i in self._items:
            i._collection = cols[i['collection']]

    @classmethod
    def load(cls, filename):
        """ Load an Items class from a GeoJSON FeatureCollection """
        with open(filename) as f:
            geoj = json.loads(f.read())
        collections = [Collection(col) for col in geoj['collections']]
        items = [Item(feature) for feature in geoj['features']]
        return cls(items, collections=collections, search=geoj.get('search'))

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

    def bbox(self):
        """ Get bounding box of search """
        if 'intersects' in self._search:
            coords = self._search['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [min(lons), min(lats), max(lons), max(lats)]
        else:
            return None

    def center(self):
        if 'intersects' in self._search:
            coords = self._search['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [(min(lats) + max(lats))/2.0, (min(lons) + max(lons))/2.0]
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
            txt += ''.join(['{:<25} '.format(s.substitute('${%s}' % p)) for p in params]) + '\n'
        return txt

    def calendar(self):
        """ Get calendar for dates """
        date_labels = {}
        dates = self.dates()
        for d in self.dates():
            sensors = self.properties('eo:platform', d)
            if len(sensors) > 1:
                date_labels[d] = 'Multiple'
            else:
                date_labels[d] = sensors[0]
        return terminal_calendar(date_labels)

    def save(self, filename):
        """ Save scene metadata """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.geojson()))

    def geojson(self):
        """ Get Items as GeoJSON FeatureCollection """
        features = [s.data for s in self._items]
        geoj = {
            'type': 'FeatureCollection',
            'features': features,
            'collections': [c.data for c in self._collections],
        }
        if self._search is not None:
            geoj['search'] = self._search
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