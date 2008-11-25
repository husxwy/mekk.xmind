# -*- coding: utf-8 -*-

"""
Prawdziwe uruchomienie
"""

from mekk.xmind import XMindDocument

OUTPUT = "test.xmind"

xmind = XMindDocument.create(u"Główna kartka", u"Luźne pomysły")
first_sheet = xmind.get_first_sheet()
root_topic = first_sheet.get_root_topic()

root_topic.add_subtopic(u"Pierwszy")
root_topic.add_subtopic(u"Drugi")
t = root_topic.add_subtopic(u"Trzeci")
t.add_subtopic(u"Trzeci i pół")
t.add_subtopic(u"Trzeci i półtora")
root_topic.add_subtopic(u"Wolnogłówny", detached = True)
t.add_subtopic(u"Wolnopodtrzeci", detached = True)
t.add_marker("flag-red")

xmind.save(OUTPUT)

xmind.pretty_print()

print "Saved to", OUTPUT