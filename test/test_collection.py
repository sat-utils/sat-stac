import json
import os
import unittest
import shutil

from satstac import __version__, STACError, Catalog, Collection, Item


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-collection')

    @classmethod
    def _tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    def open_collection(self):
        filename = os.path.join(testpath, 'catalog/eo/landsat-8-l1/catalog.json')
        return Collection.open(filename)

    def test_open(self):
        cat = self.open_collection()
        assert(cat.id == 'landsat-8-l1')

    def test_title(self):
        cat = self.open_collection()
        assert(cat.title == 'Landsat 8 L1')
        keys = cat.keywords
        assert(len(keys) == 1)
        assert(keys[0] == 'landsat')
        license = cat.license
        assert(license == 'PDDL-1.0')
        assert(len(cat.providers) == 4)
        ext = cat.extent
        assert('spatial' in ext)
        assert('temporal' in ext)

    def test_add_item(self):
        cat = Catalog.create(root='http://my.cat').save(os.path.join(self.path, 'catalog.json'))
        col = Collection.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/catalog.json'))
        cat.add_catalog(col)
        item = Item.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/item.json'))
        col.add_item(item)
        assert(item.parent().id == 'landsat-8-l1')

    def test_add_item_without_saving(self):
        col = Collection.create()
        item = Item.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/item.json'))
        with self.assertRaises(STACError):
            col.add_item(item)

    def test_add_item_with_subcatalogs(self):
        cat = Catalog.create(root='http://my.cat').save(os.path.join(self.path, 'test_subcatalogs.json'))
        col = Collection.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/catalog.json'))
        cat.add_catalog(col)
        item = Item.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/item.json'))
        col.add_item(item, filename_template='${landsat:path}/${landsat:row}/${date}/${id}.json')
        assert(item.root().id == cat.id)
        assert(item.collection().id == col.id)
        # test code using existing catalogs
        col.add_item(item, filename_template='${landsat:path}/${landsat:row}/${date}/${id}.json')
        assert(item.root().id == cat.id)