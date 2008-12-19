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
root_topic.add_subtopic(u"Linkowany").set_link("http://mekk.waw.pl")
root_topic.add_subtopic(u"Załączony").set_attachment(
    file("map_creator.py").read(), ".txt")
root_topic.add_subtopic(u"Z notką").set_note(u"""Ala ma kota
i zażółca gęślą jaźń
od wieczora do rana.""")

CODE = "40g6170ftul9bo17p1r31nqk2a"
XMP = "../../py_mekk_nozbe2xmind/src/mekk/nozbe2xmind/NozbeIconsMarkerPackage.xmp"
root_topic.add_subtopic(u"Z moim markerem").add_marker(CODE)

xmind.embed_markers(XMP)

xmind.save(OUTPUT)

xmind.pretty_print()

print "Saved to", OUTPUT
