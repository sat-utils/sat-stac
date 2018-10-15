import datetime
import json
import os
import shutil
import unittest

from stac import Item


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-item')
    filename = os.path.join(testpath, 'catalog/landsat-8-l1/item.json')

    @classmethod
    def _tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    #@classmethod
    #def setUpClass(cls):
    #    """ Configure testing class """
    #    config.DATADIR = os.path.join(testpath, config.DATADIR)

    def test_init_without_collection(self):
        with open(self.filename) as f:
            data = json.loads(f.read())
        with open(self.filename.replace('item.json', 'catalog.json')) as f:
            coldata = json.loads(f.read())
        item = Item(data)
        assert(item.id == data['id'])
        assert(item.collection is None)
        assert(item.eobands == [])
        # now put collection properties here
        data['properties'].update(coldata['properties'])
        item = Item(data)
        assert(len(item.eobands) == 11)
    
    def test_open(self):
        """ Initialize an item """
        item = Item.open(self.filename)
        dt, tm = item.properties['datetime'].split('T')
        assert(str(item.date) == dt)
        assert(item.id == item.data['id'])
        assert(item.geometry == item.data['geometry'])
        assert(str(item) == item.data['id'])
        assert(len(item.bbox) == 4)
        #assert(list(item.keys()) == ['id', 'collection', 'datetime', 'eo:platform'])

    def test_open_with_collection(self):
        item = Item.open(self.filename)
        assert(item.collection.id == 'landsat-8-l1')
        assert(len(item['eo:bands']) == 11)
        assert(item['eo:off_nadir'] == 0)

    def test_class_properties(self):
        """ Test the property functions of the Item class """
        item = Item.open(self.filename)
        l = os.path.join(os.path.dirname(item.filename), item.data['links'][0]['href'])
        assert(os.path.abspath(item.links()[0]) == os.path.abspath(l))

    def test_assets(self):
        """ Get assets for download """
        item = Item.open(self.filename)
        href = item.data['assets']['B1']['href']
        assert(item.assets['B1']['href'] == href)
        assert(item.asset('B1')['href'] == href)
        assert(item.asset('coastal')['href'] == href)

    def test_no_asset(self):
        item = Item.open(self.filename)
        assert(item.asset('no-such-asset') == None)

    def _test_download_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.download(key='thumbnail')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def _test_download(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fname = scene.download(key='MTL')
        self.assertTrue(os.path.exists(fname))
        fname = scene.download(key='MTL')
        assert(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def _test_download_paths(self):
        """ Testing of download paths and filenames """
        scene = self.get_test_scene()
        datadir = config.DATADIR
        filename = config.FILENAME
        config.DATADIR = os.path.join(testpath, '${date}')
        config.FILENAME = '${date}_${id}'
        fname = scene.download('MTL')
        _fname = os.path.join(testpath, '2017-01-01/2017-01-01_testscene_MTL.txt')
        assert(fname == _fname)
        assert(os.path.exists(fname))
        config.DATADIR = datadir
        config.FILENAME = filename
        shutil.rmtree(os.path.join(testpath, '2017-01-01'))
        assert(os.path.exists(fname) == False)

    def _test_download_nonexist(self):
        """ Test downloading of non-existent file """
        scene = self.get_test_scene()
        fname = scene.download(key='fake_asset')
        assert(fname is None)

    def _test_download_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = [scene.download(a) for a in scene.assets if a != 'fake_asset']
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))

    def _test_create_derived(self):
        """ Create single derived scene """
        scenes = [self.get_test_scene(), self.get_test_scene()]
        scene = Item.create_derived(scenes)
        assert(scene.date == scenes[0].date)
        assert(scene['c:id'] == scenes[0]['c:id'])
