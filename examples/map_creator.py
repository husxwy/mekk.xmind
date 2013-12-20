# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

"""
Prawdziwe uruchomienie
"""
from __future__ import print_function

from mekk.xmind import XMindDocument
import six

OUTPUT = "test.xmind"

xmind = XMindDocument.create(six.u("Główna kartka"), six.u("Luźne pomysły"))
first_sheet = xmind.get_first_sheet()
root_topic = first_sheet.get_root_topic()

root_topic.add_subtopic(six.u("Pierwszy"))
root_topic.add_subtopic(six.u("Drugi"))
t = root_topic.add_subtopic(six.u("Trzeci"))
t.add_subtopic(six.u("Trzeci i pół"))
t.add_subtopic(six.u("Trzeci i półtora"))
root_topic.add_subtopic(six.u("Wolnogłówny"), detached = True)
t.add_subtopic(six.u("Wolnopodtrzeci"), detached = True)
t.add_marker("flag-red")
root_topic.add_subtopic(six.u("Linkowany")).set_link("http://mekk.waw.pl")
root_topic.add_subtopic(six.u("Załączony")).set_attachment(
    file("map_creator.py").read(), ".txt")
root_topic.add_subtopic(six.u("Z notką")).set_note(six.u("""Ala ma kota
i zażółca gęślą jaźń
od wieczora do rana."""))

CODE = "40g6170ftul9bo17p1r31nqk2a"
XMP = "../../py_mekk_nozbe2xmind/src/mekk/nozbe2xmind/NozbeIconsMarkerPackage.xmp"
root_topic.add_subtopic(six.u("Z moim markerem")).add_marker(CODE)

xmind.embed_markers(XMP)

xmind.save(OUTPUT)

xmind.pretty_print()

print("Saved to", OUTPUT)
