import os
import unittest

from datetime import datetime
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

    def test_terminal_calendar(self):
        """ Get calendar """
        events = {
            datetime(2018,1,1).date(): "event1",
            datetime(2018,4,25).date(): "event2"
        }
        cal = utils.terminal_calendar(events)
        self.assertEqual(len(cal), 1136)
        self.assertTrue(' 2018 ' in cal)
        self.assertTrue(' January ' in cal)
        self.assertTrue(' March ' in cal)

    def test_empty_terminal_calendar(self):
        cal = utils.terminal_calendar({})
        print(cal)