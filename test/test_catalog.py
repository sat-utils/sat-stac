import json
import os
import unittest
import shutil

from stac import __version__, Catalog


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-catalog')

    @classmethod
    def tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    @classmethod
    def get_catalog(cls):
        """ Open existing test catalog """
        return Catalog.open(os.path.join(testpath, 'catalog'))

    @classmethod
    def create_catalog(cls, name):
        path = os.path.join(cls.path, name)
        return Catalog.create(path)

    def test_init(self):
        with open(os.path.join(testpath, 'catalog/catalog.json')) as f:
            data = json.loads(f.read())
        cat = Catalog(data)
        assert(cat.id == 'stac')

    def test_open(self):
        """ Initialize Catalog with a file """
        cat = self.get_catalog()
        assert(len(cat.keys()) == 4)
        assert(cat.id == 'stac')
        assert(len(cat.links())==3)

    def test_properties(self):
        cat = self.get_catalog()
        assert(cat.stac_version == __version__)
        assert(cat.description == 'A STAC of public datasets')

    def test_create(self):
        """ Create new catalog file """
        cat = self.create_catalog('create')
        assert(cat.id == 'stac-catalog')

    def test_create_with_keywords(self):
        path = os.path.join(testpath, 'test-catalog', 'create_with_keywords')
        desc = 'this is a catalog'
        cat = Catalog.create(path, description=desc)
        assert(cat.description == desc)

    def test_links(self):
        root = self.get_catalog()
        child = root.children()[0]
        assert(child.parent().id == root.id)

    #def _test_add_collection(self):
    #    """ Add a collection to a catalog """
    #    cat = self.create_catalog('add_collection')
    #    cat.add_collection('collection.json')