# -*- coding: utf-8 -*-

import unittest, zipfile, tempfile, os, re
from sample_maps import *

class MapCompareBase(object):
    """
    Bazowa klasa dla testów porównujących wygenerowaną mapę z wzorcem.
    Podklasa definiuje:
    - funkcję generate,
    - atrybut pattern_file
    """
    def generate(self):
        """
        Ma zwrócić obiekt document gotowy do zawołania .save
        """
        raise NotImplementedError
    def setUp(self):
        pf = self.pattern_file
        if not os.path.isfile(pf):
            pf = os.path.join("tests", pf)
        self.pattern = zipfile.ZipFile(pf, "r")
        fd, self.tfname = tempfile.mkstemp(".zip")
        self.generate().save(self.tfname)
        self.generated = zipfile.ZipFile(self.tfname, "r")
    def tearDown(self):
        self.generated.close()
        os.remove(self.tfname)
    def testSameMembers(self):
        self.assertEqual(
                         sorted(self.pattern.namelist()),
                         sorted(self.generated.namelist()),
                         )
    def testSameContent(self):
        return self._sameXml("content.xml")
    def testSameStyle(self):
        return self._sameXml("styles.xml")
    def testSameManifest(self):
        return self._sameXml("META-INF/manifest.xml")
    def testSameMeta(self):
        return self._sameXml("meta.xml")
    def _sameXml(self, name):
        pat = self.pattern.read(name)
        got = self.generated.read(name)
        pats = re.sub('id="bfbf\d+"', 'id="bfbf0000"', pat)
        gots = re.sub('id="bfbf\d+"', 'id="bfbf0000"', got)
        if not pats == gots:
            self.fail("File %s mismatch.\nOriginal:\n%s\nCreated:\n%s" % (name, pat, got))

class SimpleMapTestCase(MapCompareBase, unittest.TestCase):
    pattern_file = "simple.xmind"
    def generate(self):
        return generate_simple()

