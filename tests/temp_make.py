# -*- coding: utf-8 -*-

from mekk.xmind import XMindDocument

class Blah(object):
    def generate(self):
        doc = XMindDocument.create(u"Główny", u"Projekty")
	sheet = doc.get_first_sheet()
        root = sheet.get_root_topic()
        root.set_note("View the Help sheet for info\nwhat you can do with this map")

        style = doc.create_topic_style(fill = "#37D02B")
        #style_sub = xmw.create_topic_style(fill = "CCCCCC")

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
	
b = Blah()
x = b.generate()
x.save("simple.xmind")