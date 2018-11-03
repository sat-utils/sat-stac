import json

from .item import Item
from .utils import get_text_calendar


class Items(object):
    """ A GeoJSON FeatureCollection of STAC Items with associated Collections """

    def __init__(self, items, collections={}, search=None):
        """ Initialize with a list of Item objects """
        self._items = items
        self._collections = collections
        self._search = search

    @classmethod
    def load(cls, filename):
        """ Load an Items class from a GeoJSON FeatureCollection """
        with open(filename) as f:
            geoj = json.loads(f.read())
        items = [Item(feature) for feature in geoj['features']]
        return cls(items, collections=geoj['collections'], search=geoj.get('search'))

    def __len__(self):
        """ Number of scenes """
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted(list(set([s.date for s in self._items])))

    def collections(self):
        """ Get collection records for this list of scenes """
        return self._collections

    def bbox(self):
        """ Get bounding box of search """
        if self._search is None:
            return None
        if 'intersects' in self._search:
            coords = self._search['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [min(lons), min(lats), max(lons), max(lats)]
        else:
            return []

    def center(self):
        if self._search is None:
            return None
        if 'intersects' in self._search:
            coords = self._search['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [(min(lats) + max(lats))/2.0, (min(lons) + max(lons))/2.0]
        else:
            return 0, 0

    def platforms(self, date=None):
        """ List of all available sensors across scenes """
        if date is None:
            return list(set([i['eo:platform'] for i in self._items]))
        else:
            return list(set([i['eo:platform'] for i in self._items if i.date == date]))

    def print(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'id']
        txt = 'Items (%s):\n' % len(self._items)
        txt += ''.join(['{:<20}'.format(p) for p in params]) + '\n'
        for s in self._items:
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
        return get_text_calendar(date_labels)

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
            'collections': self._collections,
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

    def download(self, **kwargs):
        dls = []
        for i in self._items:
            fname = i.download(**kwargs)
            if fname is not None:
                dls.append(fname)
        return dls