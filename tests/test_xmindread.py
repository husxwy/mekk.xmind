# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

"""
Testy odczytu struktury mapy
"""
import unittest, os
from mekk.xmind import XMindDocument
import six

def open_doc(name):
    if not os.path.isfile(name):
        name = os.path.join("tests", name)
    return XMindDocument.open(name)

class ReadTestCase(unittest.TestCase):
    def test_simple(self):
        doc = open_doc("simple.xmind")

        sheet = doc.get_first_sheet()
        root = sheet.get_root_topic()

        self.failUnlessEqual(root.get_title(), "Projekty")
        self.failUnlessEqual(sheet.get_title(), six.u("Główny"))

        self.failUnlessEqual(root.get_note(),
                "View the Help sheet for info\nwhat you can do with this map")

        ## TODO: weryfikacja stylu
        #style = doc.create_topic_style(fill = "#37D02B")

        #from lxml import etree
        #from mekk.xmind.xmlutil import find_xpath
        #print etree.tostring(root.topic_tag, pretty_print = True)
        #print find_xpath(root.topic_tag, "xm:title")

        main_topics = list( root.get_subtopics() )
        self.failUnlessEqual(len(main_topics), 4)
        for no, topic in enumerate(main_topics):
            i = no + 1
            self.failUnlessEqual(topic.get_title(),
                                 six.u("Elemiątko %d") % i)
            self.failUnlessEqual(topic.get_embedded_id(),
                                 "b%d" % i)
            self.failUnlessEqual(topic.get_label(), "%d" % i)
            #topic.set_style(style)
            self.failUnlessEqual(topic.get_link(), "http://info.onet.pl")

            sub_topics = list( topic.get_subtopics() )
            self.failUnlessEqual(len(sub_topics), 2)
            for mo, subtopic in enumerate(sub_topics):
                j = mo + 1
                self.failUnlessEqual(subtopic.get_title(),
                                     six.u("Subelemiątko %d/%d") % (i,j))
                self.failUnlessEqual(subtopic.get_embedded_id(),
                                     six.u("a%da%d") % (i,j))
                markers = list( subtopic.get_markers() )
                if j < 2:
                    self.failUnlessEqual(markers, ["task-start", "other-people"])
                else:
                    self.failUnlessEqual(markers, ["task-start"])

        legend = sheet.get_legend()
        # TODO: test czytania legendy
        legend.add_marker("task-start", six.u("Dzień dobry"))
        #legend.add_marker("other-people", u"Do widzenia")
