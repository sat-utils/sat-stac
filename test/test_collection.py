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

    #@classmethod
    #def get_collection(cls):
    #    """ Open existing test catalog """
    #    return Catalog.open(os.path.join(testpath, 'catalog'))

    #@classmethod
    #def create_catalog(cls, name):
    #    path = os.path.join(cls.path, name)
    #    return Catalog.create(path)

    def test_init(self):
        with open(os.path.join(testpath, 'catalog/catalog.json')) as f:
            data = json.loads(f.read())
        cat = Collection(data)
        assert(cat.id == 'stac')

