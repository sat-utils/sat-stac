


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