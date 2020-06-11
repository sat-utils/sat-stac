import json
import os
import unittest
import shutil

from satstac import __version__, Catalog, STACError, Item


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
        return Catalog.open(os.path.join(testpath, 'catalog/catalog.json'))

    @classmethod
    def create_catalog(cls, name):
        path = os.path.join(cls.path, name)
        return Catalog.create(path)

    def test_init(self):
        with open(os.path.join(testpath, 'catalog/catalog.json')) as f:
            data = json.loads(f.read())
        cat = Catalog(data)
        assert(cat.id == 'stac-catalog')

    def test_open(self):
        """ Initialize Catalog with a file """
        cat = self.get_catalog()
        assert(len(cat._data.keys()) == 4)
        assert(cat.id == 'stac-catalog')
        assert(len(cat.links())==3)

    def test_properties(self):
        cat = self.get_catalog()
        assert(cat.stac_version == '1.0.0-beta.1')
        assert(cat.description == 'An example STAC catalog')

    def test_create(self):
        """ Create new catalog file """
        cat = Catalog.create()
        assert(cat.id == 'stac-catalog')

    def test_create_with_keywords(self):
        path = os.path.join(testpath, 'test-catalog', 'create_with_keywords')
        desc = 'this is a catalog'
        cat = Catalog.create(path, description=desc)
        assert(cat.description == desc)

    def test_links(self):
        root = self.get_catalog()
        child = [c for c in root.children()][0]
        assert(child.parent().id == root.id)

    def test_get_catalogs(self):
        catalogs = [i for i in self.get_catalog().catalogs()]
        assert(len(catalogs) == 4)

    def test_get_collections(self):
        collections = [i for i in self.get_catalog().collections()]
        assert(len(collections) == 2)
        assert(collections[0].id in ['landsat-8-l1', 'sentinel-s2-l1c'])
        assert(collections[1].id in ['landsat-8-l1', 'sentinel-s2-l1c'])

    def test_get_items(self):
        items = [i for i in self.get_catalog().items()]
        assert(len(items) == 2)

    def test_add_catalog(self):
        cat = Catalog.create(root='http://my.cat').save(os.path.join(self.path, 'catalog.json'))
        col = Catalog.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/catalog.json'))
        cat.add_catalog(col)
        child = [c for c in cat.children()][0]
        assert(child.id == col.id)

    def test_add_catalog_without_saving(self):
        cat = Catalog.create()
        with self.assertRaises(STACError):
           cat.add_catalog({})
