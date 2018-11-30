import os
import unittest
#import satsearch.config as config
#from satsearch.scene import Scenes
from satstac import utils


class Test(unittest.TestCase):

    path = os.path.dirname(__file__)

    remote_url = 'https://landsat-stac.s3.amazonaws.com/catalog.json'

    def test_dict_merge(self):
        dict1 = {
            'key1': {
                'subkey1': 'val'
            }
        }
        dict2 = {
            'key1': {
                'subkey2': 'val'
            },
            'key2': 'val'
        }
        _dict = utils.dict_merge(dict1, dict2)
        assert('key1' in _dict)
        assert('key2' in _dict)
        assert('subkey1' in _dict['key1'])
        assert('subkey2' in _dict['key1'])
        _dict = utils.dict_merge(dict1, dict2, add_keys=False)
        assert('key1' in _dict)
        assert('key2' not in _dict)
        assert('subkey1' in _dict['key1'])
        assert('subkey2' not in _dict['key1'])

    def test_download_nosuchfile(self):
        with self.assertRaises(Exception):
            utils.download_file('http://nosuchfile')

    def test_get_s3_signed_url(self):
        url = utils.get_s3_signed_url(self.remote_url)
        assert(len(url) == 2)

    def test_get_s3_public_url(self):
        envs = dict(os.environ)
        if 'AWS_ACCESS_KEY_ID' in envs:
            del os.environ['AWS_ACCESS_KEY_ID']
        if 'AWS_BUCKET_ACCESS_KEY_ID' in envs:
            del os.environ['AWS_BUCKET_ACCESS_KEY_ID']        
        url = utils.get_s3_signed_url(self.remote_url)
        assert(len(url) == 2)
        assert(url[0] == self.remote_url)
        assert(url[1] is None)
        os.environ.clear()
        os.environ.update(envs)

    def _test_text_calendar(self):
        """ Get calendar """
        scenes = self.load_scenes()
        cal = scenes.text_calendar()
        self.assertEqual(len(cal), 576)
        self.assertTrue(' 2018 ' in cal)
        self.assertTrue(' January ' in cal)
        self.assertTrue(' March ' in cal)

    def _test_text_calendar_multiyear(self):
        scenes = self.load_scenes()
        scenes[0].feature['properties']['datetime'] = '2010-02-01T00:00:00.000Z'
        cal = scenes.text_calendar()
        self.assertEqual(len(cal), 16654)
        self.assertTrue(' 2016 ' in cal)
        self.assertTrue(' 2017 ' in cal)
