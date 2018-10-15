import json
import os
import shutil
import unittest
from stac.thing import Thing, STACError


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-thing')
    fname = os.path.join(testpath, 'test-thing.json')

    @classmethod
    def tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    def get_thing(self):
        """ Configure testing class """
        with open(self.fname) as f:
            data = json.loads(f.read())
        return Thing(data)

    def test_init(self):
        thing1 = self.get_thing()
        assert(thing1.id == 'test-thing-id')
        assert(len(thing1.links()) == 1)
        assert(len(thing1.links('self')) == 1)
        data = thing1.data
        del data['links']
        thing2 = Thing(data)
        assert(thing2.links() == [])
        with self.assertRaises(STACError):
            thing2.save()
        print(thing1)

    def test_open(self):
        thing1 = self.get_thing()
        thing2 = Thing.open(self.fname)
        assert(thing1.id == thing2.id)
        assert(
            os.path.basename(thing1.links()[0]) 
            == os.path.basename(thing2.links()[0])
        )

    def test_keys(self):
        thing = self.get_thing()
        assert('id' in thing.keys())
        assert('links' in thing.keys())

    def test_links(self):
        thing = self.get_thing()
        assert('links' in thing.keys())
        del thing.data['links']
        assert('links' not in thing.keys())
        assert(thing.links() == [])

    def test_getitem(self):
        thing = self.get_thing()
        assert(thing['some_property'] is None)
    
    def test_save(self):
        thing = Thing.open(self.fname)
        thing.save()
        fout = os.path.join(self.path, 'test-save.json')
        thing.save_as(fout)
        assert(os.path.exists(fout))
