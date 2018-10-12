import os
import unittest
import shutil
from stac.catalog import Catalog


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test_catalog')

    @classmethod
    def tearDownClass(cls):
        """ Remove test files """
        shutil.rmtree(cls.path)

    @classmethod
    def get_catalog(cls):
        filename = os.path.join(testpath, 'catalog', 'catalog.json')
        return Catalog(filename)

    @classmethod
    def create_catalog(cls, name):
        path = os.path.join(testpath, 'test_catalog', name)
        return Catalog.create(path)

    def test_init(self):
        """ Initialize Catalog with a file """
        cat = self.get_catalog()
        print(cat.keys())
        assert(len(cat.keys()) == 4)
        assert(cat['id'] == 'stac')
        assert(len(cat['links'])==3)

    def test_create(self):
        """ Create new catalog file """
        cat = self.create_catalog('create')
        assert(os.path.exists(cat.filename))
        assert(cat['id'] == 'stac-catalog')

    def test_create_with_keywords(self):
        path = os.path.join(testpath, 'test_catalog', 'create_with_keywords')
        cat = Catalog.create(path, title='some title')
        assert(cat['title'] == 'some title')

    def test_add_collection(self):
        """ Add a collection to a catalog """
        cat = self.create_catalog('add_collection')
        cat.add_collection('collection.json')
