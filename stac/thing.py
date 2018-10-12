import json


class STACError(Exception):
    pass


class Thing(object):

    def __init__(self, arg):
        """ Init thing (Collection or Item) with JSON OR a JSON string OR filename/URL string """
        self.arg = arg
        self.data = None

    def get(self):
        if self.data is None:
            if isinstance(self.arg, str):
                try:
                    self.data = json.loads(self.arg)
                except Exception as err:
                    try:
                        # if not JSON read from file
                        with open(self.arg) as f:
                            self.data = json.loads(f.read())
                    except Exception as err:
                        raise STACError('Error loading JSON %s' % err)
            else:
                self.data = self.arg
        return self.data         

    def __getitem__(self, key):
        if key in ['properties', 'assets']:
            default = {}
        elif key in ['links']:
            default = []
        else:
            default = None
        return self.get().get(key, default)
    
    #def get(self, key, default=None):
    #    return self.get().get(key, default)

    @property
    def id(self):
        return self['id']

    @property
    def properties(self):
        return self.get('properties', {}).keys()

    @property
    def assets(self):
        """ Return dictionary of assets """
        return self.get('assets', {})

    @property
    def links(self):
        """ Return dict list of links """
        return self.get('links', [])

