# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

"""
Zbiór funkcji generujących pliki służące do testów. Funkcje są normalnie używane
przy testach regresywnych (różne unittesty w tym katalogu) ale mogą też służyć do
ich inicjalnego utworzenia.

Każdy zwraca obiekt Document gotowy do zapisu.
"""

from mekk.xmind import XMindDocument

def generate_simple():
    doc = XMindDocument.create(u"Główny", u"Projekty")
    sheet = doc.get_first_sheet()
    root = sheet.get_root_topic()
    root.set_note("View the Help sheet for info\nwhat you can do with this map")

    style = doc.create_topic_style(fill = "#37D02B")
    #style_sub = doc.create_topic_style(fill = "CCCCCC")

    for i in range(1,5):
        topic = root.add_subtopic(u"Elemiątko %d" % i, "b%d" % i)
        topic.set_label("%d" % i)
        topic.set_style(style)
        topic.set_link("http://info.onet.pl")
        for j in range(1,3):
            subtopic = topic.add_subtopic(u"Subelemiątko %d/%d" % (i,j),
                                          u"a%da%d" % (i,j))
            subtopic.add_marker("task-start")
            if j < 2:
                subtopic.add_marker("other-people")

    legend = sheet.get_legend()
    legend.add_marker("task-start", u"Dzień dobry")
    legend.add_marker("other-people", u"Do widzenia")

    return doc

if __name__ == "__main__":
    generate_simple().save("simple.xmind")
