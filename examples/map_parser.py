from __future__ import print_function
# -*- coding: utf-8 -*-
# (c) 2008-2010, Marcin Kasperski

from mekk.xmind import XMindDocument

def parse_and_print(file_name):
    xmind = XMindDocument.open(file_name)

    sheet = xmind.get_first_sheet()
    print("Sheet title: ", sheet.get_title())

    root = sheet.get_root_topic()
    print("Root title: ", root.get_title())
    print("Root note: ", root.get_note())

    for topic in root.get_subtopics():
        print("* ", topic.get_title())
        print("   label: ", topic.get_label())
        print("   link: ", topic.get_link())
        print("   markers: ", list(topic.get_markers()))
        # topic.get_subtopics()

    #legend = sheet.get_legend()

if __name__ == "__main__":
    parse_and_print("test.xmind")
    parse_and_print("test_manual.xmind")
