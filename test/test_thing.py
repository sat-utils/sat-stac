import os
import json
import unittest
from stac.thing import Thing


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    fname = os.path.join(testpath, 'test-thing.json')

    def get_thing(self):
        """ Configure testing class """
        with open(self.fname) as f:
            data = json.loads(f.read())
        return Thing(data)

    def test_init(self):
        thing1 = self.get_thing()
        assert(thing1.id == 'test-thing-id')
        assert(len(thing1.links) == 1)
        data = thing1.data
        del data['links']
        thing2 = Thing(data)
        assert(thing2.links == [])

    def test_open(self):
        thing1 = self.get_thing()
        thing2 = Thing.open(self.fname)
        assert(thing1.id == thing2.id)
        assert(thing1.links == thing2.links)

    def test_keys(self):
        thing = self.get_thing()
        assert('id' in thing.keys())
        assert('links' in thing.keys())

    def test_links(self):
        thing = self.get_thing()
        assert('links' in thing.keys())
        del thing.data['links']
        assert('links' not in thing.keys())
        assert(thing.links == [])

    def test_getitem(self):
        thing = self.get_thing()
        assert(thing['some_property'] is None)
