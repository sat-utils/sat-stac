import datetime
import json
import os
import shutil
import unittest

from satstac import Item

testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-item')
    filename_template = os.path.join(path, '${collection}/${id}')
    filename = os.path.join(testpath, 'catalog/eo/landsat-8-l1/item.json')

    @classmethod
    def tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    def test_init_without_collection(self):
        with open(self.filename) as f:
            data = json.loads(f.read())
        with open(self.filename.replace('item.json', 'catalog.json')) as f:
            coldata = json.loads(f.read())
        item = Item(data)
        assert(item.id == data['id'])
        assert(item.collection() is None)
    
    def test_open(self):
        """ Initialize an item """
        item = Item.open(self.filename)
        dt, tm = item.properties['datetime'].split('T')
        assert(str(item.date) == dt)
        assert(item.id == item._data['id'])
        assert(item.geometry == item._data['geometry'])
        assert(str(item) == item._data['id'])
        assert(len(item.bbox) == 4)
        #assert(list(item.keys()) == ['id', 'collection', 'datetime', 'eo:platform'])

    def test_open_with_collection(self):
        item = Item.open(self.filename)
        assert(item.collection().id == 'landsat-8-l1')
        sum = item.collection().summaries
        assert(len(sum) == 4)
        assert(len(sum['platform']) == 1)
        assert('landsat-8' in sum['platform'])

    def test_class_properties(self):
        """ Test the property functions of the Item class """
        item = Item.open(self.filename)
        l = os.path.join(os.path.dirname(item.filename), item._data['links'][0]['href'])
        assert(os.path.abspath(item.links()[0]) == os.path.abspath(l))

    def test_assets(self):
        """ Get assets for download """
        item = Item.open(self.filename)
        href = item._data['assets']['B1']['href']
        assert(item.assets['B1']['href'] == href)
        assert(item.asset('B1')['href'] == href)
        assert(item.asset('coastal')['href'] == href)

    def test_no_asset(self):
        item = Item.open(self.filename)
        assert(item.asset('no-such-asset') == None)

    def test_get_path(self):
        """ Test string templating with item fields """
        item = Item.open(self.filename)
        st = item.get_path('${collection}/${date}')
        assert(st == 'landsat-8-l1/2020-06-11')
        st = item.get_path('nosub')
        assert(st == 'nosub')

    def test_download_thumbnail(self):
        """ Get thumbnail for item """
        item = Item.open(self.filename)
        fname = item.download(key='thumbnail', filename_template=self.filename_template)
        assert(os.path.exists(fname))

    def test_download(self):
        """ Retrieve a data file """
        item = Item.open(self.filename)
        fname = item.download(key='MTL', filename_template=self.filename_template)
        assert(os.path.exists(fname))
        #fname = item.download(key='MTL', filename_template=self.filename_template)
        #assert(os.path.exists(fname))

    def test_download_assets(self):
        """ Retrieve multiple data files """
        item = Item.open(self.filename)
        fnames = item.download_assets(keys=['MTL', 'ANG'], filename_template=self.filename_template)
        for f in fnames:
            assert(os.path.exists(f))

    def test_download_nonexist(self):
        """ Test downloading of non-existent file """
        item = Item.open(self.filename)
        fname = item.download(key='fake_asset', filename_template=self.filename_template)
        assert(fname is None)
