# -*- coding: utf-8 -*-

import unittest, zipfile, tempfile, os
from mekk.xmind import XMindDocument

class MapCompareBase(object):
    """
    Bazowa klasa dla testów porównujących wygenerowaną mapę z wzorcem.
    Podklasa definiuje:
    - funkcję generate,
    - atrybut pattern_file
    """
    def __init__(self, pattern_file):
        self.pattern = zipfile.ZipFile(self.pattern_file, "r")
    def generate(self):
        """
        Ma zwrócić obiekt document gotowy do zawołania .save
        """
        raise NotImplementedError
    def setUpClass(self):
        fd, self.tfname = tempfile.mkstemp(".zip")
        self.generate().save(self.tfname)
        self.generated = zipfile.ZipFile(self.tfname, "r")
    def tearDownClass(self):
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
        self.assertEqual(pat, got)

class SimpleMapTestCase(unittest.TestCase):
    pattern_file = "blabla.xmind"
    def generate(self):
        doc = XMindDocument.create("Główny", "Projekty")
        root = doc.get_first_sheet().get_root_topic()
        root.set_note("View the Help sheet for info\nwhat you can do with this map")

        style = xmw.create_topic_style(fill = "#37D02B")
        #style_sub = xmw.create_topic_style(fill = "CCCCCC")

        for i in range(1,5):
            topic = root.add_subtopic("Elemiątko %d" % i)
            topic.set_label("%d" % i)
            topic.set_style(style)
            for j in range(1,3):
                subtopic = topic.add_subtopic("Subelemiątko %d/%d" % (i,jk))
                subtopic.add_marker("task-start")
                if j < 2:
                    subtopic.add_marker("other-people")

        legend = sheet.get_legend()
        legend.add_marker("task-start", "Dzień dobry")
        legend.add_marker("other-people", "Do widzenia")

        return doc