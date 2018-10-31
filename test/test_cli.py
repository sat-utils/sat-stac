import os
import sys
import unittest

from shlex import split
from shutil import rmtree
from datetime import datetime as dt

from satstac.cli import parse_args, cli
from satstac import Catalog

testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    def test_parse_no_args(self):
        with self.assertRaises(SystemExit):
            parse_args([''])
        with self.assertRaises(SystemExit):
            parse_args(['-h'])

    def test_parse_args(self):
        input = "create testid 'this is a description' --endpoint 'https://my.cat'"
        args = parse_args(split(input))
        assert(len(args) == 7)
        assert(args['endpoint'] == 'https://my.cat')
        assert(args['id'] == 'testid')

    def test_cli_create(self):
        input = "sat-stac create cat 'this is a description' --endpoint 'https://my.cat'"
        sys.argv = split(input)
        cli()
        assert(os.path.exists('catalog.json'))
        input = "sat-stac create subcat 'this is another description' --root catalog.json"
        sys.argv = split(input)
        cli()
        assert(os.path.exists('subcat/catalog.json'))
        rmtree('subcat')
        os.remove('catalog.json')

    def test_cli_publish(self):
        cat = Catalog.create(root='https://my.cat').save_as('catalog.json')
        input = "sat-stac publish catalog.json https://my.kitten"
        sys.argv = split(input)
        cli()
        cat = Catalog.open('catalog.json')
        assert(cat.links('self')[0] == 'https://my.kitten/catalog.json')
        os.remove('catalog.json')