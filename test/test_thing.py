import datetime
import os
import json
import unittest
#import satsearch.config as config
from stac.thing import Thing


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    cat = os.path.join(testpath, 'test-catalog', 'catalog.json')

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        #config.DATADIR = os.path.join(testpath, config.DATADIR)
        pass

    def test_init_from_file_string(self):
        """ Init Thing from filename """
        """ Initialize an item """
        th = Thing(self.cat)
        assert(th.id == 'stac')

    def test_init_from_json_string(self):
        """ Init Thing from JSON string """
        with open(self.cat) as f:
            cat = f.read()
        th = Thing(cat)
        assert(th.id == 'stac')

    def test_init_from_json(self):
        """ Init Thing from JSON """
        with open(self.cat) as f:
            cat = json.loads(f.read())
        th = Thing(cat)
        assert(th.id == 'stac')
