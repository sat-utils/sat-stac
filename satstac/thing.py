import json
import os
import requests

from .version import __version__
from .utils import mkdirp, get_s3_signed_url


class STACError(Exception):
    pass


class Thing(object):

    def __init__(self, data, filename=None):
        """ Initialize a new class with a dictionary """
        self.filename = filename
        self.data = data
        if 'links' not in self.data.keys():
            self.data['links'] = []
        self._root = None

    def __repr__(self):
        return self.id

    @classmethod
    def open(cls, filename):
        """ Open an existing JSON data file """
        # TODO - open remote URLs
        if filename[0:5] == 'https':
            resp = requests.get(filename)
            if resp.status_code == 200:
                dat = resp.text
            else:
                # try signed URL
                url, headers = get_s3_signed_url(filename)
                resp = requests.get(url, headers=headers)
                if resp.status_code == 200:
                    dat = resp.text
                else:
                    raise STACError('Unable to open file %s' % filename)
        else:
            dat = open(filename).read()
        dat = json.loads(dat)
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
        rels = ['self', 'root', 'parent', 'child', 'collection', 'item']
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
        fname = self.filename
        if self.filename[0:5] == 'https':
            # use signed URL
            signed_url, signed_headers = get_s3_signed_url(self.filename, rtype='PUT',
                                                           public=True, content_type='application/json')
            resp = requests.put(signed_url, data=json.dumps(self.data), headers=signed_headers)
            if resp.status_code != 200:
                raise STACError('Unable to save file to %s: %s' % (self.filename, resp.text))
        else:
            # local file save
            mkdirp(os.path.dirname(fname))
            with open(fname, 'w') as f:
                f.write(json.dumps(self.data))
        return self

    def save_as(self, filename):
        """ Write a catalog file to a new file """
        self.filename = filename
        # TODO - if this is a root then add root link and self links to itself
        if self._root is not None:
            self.add_link('self', os.path.join(self._root, os.path.basename(filename)))
            self.add_link('root', './%s' % os.path.basename(filename))
        self.save()
        return self

    def publish(self, endpoint, root):
        """ Update self link with endpoint """
        if self.filename is None:
            raise STACError('No filename, use save_as() before publishing')
        # keep everything except self and root
        links = [l for l in self.data['links'] if l['rel'] not in ['self', 'root']]
        to_item = os.path.relpath(self.filename, os.path.dirname(root))
        to_root = os.path.relpath(root, os.path.dirname(self.filename))
        links.insert(0, {'rel': 'root', 'href': to_root})
        links.insert(0, {'rel': 'self', 'href': os.path.join(endpoint, to_item)})
        self.data['links'] = links
        self.save()
