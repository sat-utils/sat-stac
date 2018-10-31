import json
import os

from .version import __version__
from .utils import mkdirp


class STACError(Exception):
    pass


class Thing(object):

    def __init__(self, data, filename=None):
        """ Initialize a new class with a dictionary """
        self.filename = filename
        self.data = data
        if 'links' not in self.data.keys():
            self.data['links'] = []

    def __repr__(self):
        return self.id

    @classmethod
    def open(cls, filename):
        """ Open an existing JSON data file """
        # TODO - open remote URLs
        with open(filename) as f:
            dat = json.loads(f.read())
        return cls(dat, filename=filename)

    @property
    def id(self):
        """ Return id of this entity """
        return self.data['id']

    @property
    def path(self):
        """ Return path to this catalog file (None if no filename set) """
        return os.path.dirname(self.filename) if self.filename else None

    def keys(self):
        """ Get keys from catalog """
        return self.data.keys()

    def links(self, rel=None):
        """ Get links for specific rel type """
        links = self.data.get('links', [])
        if rel is not None:
            links = [l for l in links if l.get('rel') == rel]
        links = [l['href'] for l in links]
        if self.filename is not None:
            _links = []
            for l in links:
                if not os.path.isabs(l) and l[0:5] != 'https':
                    ## link is relative to the location of this Thing
                    fname = os.path.join(os.path.dirname(self.filename), l)
                    _links.append(os.path.abspath(fname))
                else:
                    _links.append(l)
            links = _links
        return links

    def root(self):
        """ Get root link """
        links = self.links('root')
        return self.open(links[0]) if len(links) == 1 else []

    def parent(self):
        """ Get parent link """
        links = self.links('parent')
        return self.open(links[0]) if len(links) == 1 else []

    def add_link(self, rel, link, type=None, title=None):
        """ Add a new link """
        # if this link already exists do not add it
        for l in self.data['links']:
            if l['rel'] == rel and l['href'] == link:
                return
        l = {'rel': rel, 'href': link}
        if type is not None:
            l['type'] = type
        if title is not None:
            l['title'] = title
        self.data['links'].append(l)

    def clean_hierarchy(self):
        """ Clean links of self, parent, and child links (for moving and publishing) """
        rels = ['self', 'root', 'parent', 'child', 'collection']
        links = []
        for l in self.data['links']:
            if l['rel'] not in rels:
                links.append(l)
        self.data['links'] = links

    def __getitem__(self, key):
        """ Get key from properties """
        props = self.data.get('properties', {})
        return props.get(key, None)

    def save(self):
        """ Write a catalog file """
        if self.filename is None:
            raise STACError('No filename, use save_as()')
        mkdirp(os.path.dirname(self.filename))
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.data))
        return self

    def save_as(self, filename, root=None):
        """ Write a catalog file to a new file """
        self.filename = filename
        # TODO - is this the best place for root?
        if root is not None:
            self.add_link('self', os.path.join(root, os.path.basename(filename)))
            self.add_link('root', './%s' % os.path.basename(filename))
        self.save()
        return self

    def publish(self, endpoint):
        """ Update self link with endpoint """
        if self.filename is None:
            raise STACError('No filename, use save_as() before publishing')
        links = [l for l in self.data['links'] if l['rel'] != 'self']
        
        relpath = os.path.relpath(self.filename, os.path.dirname(self.links('root')[0]))
        slink = os.path.join(endpoint, relpath)
        links.insert(0, {'rel': 'self', 'href': slink})
        self.data['links'] = links
        self.save()