import json
import os
import unittest
import shutil

from stac import __version__, Collection


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-collection')

    @classmethod
    def _tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    def open_collection(self):
        filename = os.path.join(testpath, 'catalog/landsat-8-l1/catalog.json')
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
        version = cat.version
        assert(version == '0.1.0')
        license = cat.license
        assert(license == 'PDDL-1.0')
        assert(len(cat.providers) == 4)
        ext = cat.extent
        assert('spatial' in ext)
        assert('temporal' in ext)
        assert(len(cat.properties))
