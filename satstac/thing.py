import json
import os
import requests

from logging import getLogger
from urllib.parse import urljoin
from .version import __version__
from .utils import mkdirp, get_s3_signed_url


logger = getLogger(__name__)


class STACError(Exception):
    pass


class Thing(object):

    def __init__(self, data, filename=None):
        """ Initialize a new class with a dictionary """
        self.filename = filename
        self._data = data
        if 'id' not in data:
            raise STACError('ID is required')
        if 'links' not in self._data.keys():
            self._data['links'] = []

    def __repr__(self):
        return self.id

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
        """ Open an existing JSON data file """
        logger.debug('Opening %s' % filename)
        if filename[0:5] == 'https':
            try:
                dat = cls.open_remote(filename)
            except STACError as err:
                # try signed URL
                url, headers = get_s3_signed_url(filename)
                dat = cls.open_remote(url, headers)
        else:
            if os.path.exists(filename):
                dat = open(filename).read()
                dat = json.loads(dat)
            else:
                raise STACError('%s does not exist locally' % filename)
        return cls(dat, filename=filename)

    def __getitem__(self, key):
        """ Get key from properties """
        props = self._data.get('properties', {})
        return props.get(key, None)

    @property
    def id(self):
        """ Return id of this entity """
        return self._data['id']

    @property
    def path(self):
        """ Return path to this catalog file (None if no filename set) """
        return os.path.dirname(self.filename) if self.filename else None

    def links(self, rel=None):
        """ Get links for specific rel type """
        links = self._data.get('links', [])
        if rel is not None:
            links = [l for l in links if l.get('rel') == rel]
        links = [l['href'] for l in links]
        if self.filename is not None:
            _links = []
            for l in links:
                if os.path.isabs(l) or l[0:4] == 'http':
                    # if absolute or https 
                    link = l
                else:
                    # relative path
                    if self.filename[0:4] == 'http':
                        link = urljoin(os.path.dirname(self.filename) + '/', l)
                    else: 
                        link = os.path.abspath(os.path.join(os.path.dirname(self.filename), l))
                _links.append(link)
            links = _links
        return links

    def root(self):
        """ Get root link """
        links = self.links('root')
        if len(links) == 1:
            return self.open(links[0])
        elif len(links) == 0:
            # i'm the root of myself
            return self
        else:
            raise STACError('More than one root provided')

    def parent(self):
        """ Get parent link """
        links = self.links('parent')
        if len(links) == 1:
            return self.open(links[0])
        elif len(links) == 0:
            return None
        else:
            raise STACError('More than one parent provided')

    def add_link(self, rel, link, type=None, title=None):
        """ Add a new link """
        # if this link already exists do not add it
        for l in self._data['links']:
            if l['rel'] == rel and l['href'] == link:
                return
        l = {'rel': rel, 'href': link}
        if type is not None:
            l['type'] = type
        if title is not None:
            l['title'] = title
        self._data['links'].append(l)


    def clean_hierarchy(self):
        """ Clean links of self, parent, and child links (for moving and publishing) """
        rels = ['self', 'root', 'parent', 'child', 'collection', 'item']
        links = []
        for l in self._data['links']:
            if l['rel'] not in rels:
                links.append(l)
        self._data['links'] = links

    def save(self, filename=None):
        """ Write a catalog file """
        if filename is not None:
            self.filename = filename
        if self.filename is None:
            raise STACError('No filename provided, specify with filename keyword')
        logger.debug('Saving %s as %s' % (self.id, self.filename))
        fname = self.filename
        if self.filename[0:5] == 'https':
            # use signed URL
            signed_url, signed_headers = get_s3_signed_url(self.filename, rtype='PUT',
                                                           public=True, content_type='application/json')
            resp = requests.put(signed_url, data=json.dumps(self._data), headers=signed_headers)
            if resp.status_code != 200:
                raise STACError('Unable to save file to %s: %s' % (self.filename, resp.text))
        else:
            # local file save
            mkdirp(os.path.dirname(fname))
            with open(fname, 'w') as f:
                f.write(json.dumps(self._data))
        return self