from stac.catalog import Catalog


class Collection(Catalog):

    def __init__(self, collection):
        """ Initialize a scene object """

        # determine common_name to asset mapping
        # it will map if an asset contains only a single band
        '''
        bands = self.eobands
        band_to_name = {b: bands[b]['common_name'] for b in bands if bands[b].get('common_name', None)}
        self.name_to_band = {}
        for a in self.assets:
            _bands = self.assets[a].get('eo:bands', [])
            if len(_bands) == 1 and _bands[0] in band_to_name:
                self.name_to_band[band_to_name[_bands[0]]] = _bands[0]
        '''
        self.filenames = {}

    @property
    def title(self):
        return self.data.get('title', '')

    @property
    def keywords(self):
        return self.data.get('keywords', [])

    @property
    def version(self):
        return self.data.get('version', '')

    @property
    def license(self):
        return self.data.get('license', '')

    @property
    def provider(self):
        return self.data.get('provider', [])

    @property
    def extent(self):
        return self.data.get('extent', {})

    @property
    def properties(self):
        """ Get properties """
        return self.data.get('properties', {})
