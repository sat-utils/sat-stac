import unittest


class _Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = testpath
'''
    def load_scenes(self):
        return Items.load(os.path.join(testpath, 'scenes.geojson'))

    def test_load(self):
        """ Initialize Scenes with list of Scene objects """
        scenes = self.load_scenes()
        self.assertEqual(len(scenes), 2)
        self.assertTrue(isinstance(scenes.scenes[0], Item))

    def test_save(self):
        """ Save scenes list """
        scenes = self.load_scenes()
        fname = os.path.join(testpath, 'save-test.json')
        scenes.save(fname)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_print_scenes(self):
        """ Print summary of scenes """
        scenes = self.load_scenes()
        scenes.print_scenes()

    def test_dates(self):
        """ Get dates of all scenes """
        scenes = self.load_scenes()
        dates = scenes.dates()
        self.assertEqual(len(dates), 1)

    def test_text_calendar(self):
        """ Get calendar """
        scenes = self.load_scenes()
        cal = scenes.text_calendar()
        self.assertTrue(len(cal) > 250)

    def test_download_thumbnails(self):
        """ Download all thumbnails """
        scenes = self.load_scenes()
        fnames = scenes.download(key='thumbnail')
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        #shutil.rmtree(os.path.join(testpath, 'landsat-8-l1'))

    def test_filter(self):
        scenes = self.load_scenes()
        scenes.filter('eo:platform', ['landsat-8'])
        assert(len(scenes) == 1)

    def test_download(self):
        """ Download a data file from all scenes """
        scenes = self.load_scenes()
        
        fnames = scenes.download(key='MTL')
        assert(len(fnames) == 1)
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        #shutil.rmtree(os.path.join(testpath, 'landsat-8-l1'))
'''