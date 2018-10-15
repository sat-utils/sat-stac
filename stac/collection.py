from stac.catalog import Catalog


class Collection(Catalog):

    '''
    def __init__(self, *args, **kwargs):
        """ Initialize a scene object """
        super(Collection, self).__init__(*args, **kwargs)
        # determine common_name to asset mapping
        # it will map if an asset contains only a single band
    '''

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
        return self.data.get('license')

    @property
    def providers(self):
        return self.data.get('providers', [])

    @property
    def extent(self):
        return self.data.get('extent')

    @property
    def properties(self):
        """ Get dictionary of properties """
        return self.data.get('properties', {})
