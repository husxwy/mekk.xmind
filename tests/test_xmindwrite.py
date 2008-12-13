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
    def generate(self):
        """
        Ma zwrócić obiekt document gotowy do zawołania .save
        """
        raise NotImplementedError
    def setUp(self):
        self.pattern = zipfile.ZipFile(self.pattern_file, "r")
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
        if not pat == got:
            self.fail("File %s mismatch.\nOriginal:\n%s\nCreated:\n%s" % (name, pat, got))
        self.assertEqual(pat, got)

class SimpleMapTestCase(MapCompareBase, unittest.TestCase):
    pattern_file = "simple.xmind"
    def generate(self):
        doc = XMindDocument.create(u"Główny", u"Projekty")
        sheet = doc.get_first_sheet()
        root = sheet.get_root_topic()
        root.set_note("View the Help sheet for info\nwhat you can do with this map")

        style = doc.create_topic_style(fill = "#37D02B")
        #style_sub = doc.create_topic_style(fill = "CCCCCC")

        for i in range(1,5):
            topic = root.add_subtopic(u"Elemiątko %d" % i)
            topic.set_label("%d" % i)
            topic.set_style(style)
            topic.set_link("http://info.onet.pl")
            for j in range(1,3):
                subtopic = topic.add_subtopic(u"Subelemiątko %d/%d" % (i,j))
                subtopic.add_marker("task-start")
                if j < 2:
                    subtopic.add_marker("other-people")

        legend = sheet.get_legend()
        legend.add_marker("task-start", u"Dzień dobry")
        legend.add_marker("other-people", u"Do widzenia")

        return doc

