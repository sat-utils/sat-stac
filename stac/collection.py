from stac.catalog import Catalog


class Collection(Catalog):

    def __init__(self, collection):
        """ Initialize a scene object """
        self.collection = collection

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

