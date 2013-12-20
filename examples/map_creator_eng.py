from __future__ import print_function
# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.xmind import XMindDocument
import six

OUTPUT = "test_eng.xmind"

xmind = XMindDocument.create(six.u("First sheet title"), six.u("Root subject"))
first_sheet = xmind.get_first_sheet()
root_topic = first_sheet.get_root_topic()

root_topic.add_subtopic(six.u("First item"))
root_topic.add_subtopic(six.u("Second item"))
t = root_topic.add_subtopic(six.u("Third item"))
t.add_subtopic(six.u("Second level - 1"))
t.add_subtopic(six.u("Second level - 2"))
root_topic.add_subtopic(six.u("Detached topic"), detached = True)
t.add_subtopic(six.u("Another detached"), detached = True)
t.add_marker("flag-red")
root_topic.add_subtopic(six.u("Link example")).set_link("http://mekk.waw.pl")
root_topic.add_subtopic(six.u("Attachment example")).set_attachment(
    file("map_creator.py").read(), ".txt")
root_topic.add_subtopic(six.u("With note")).set_note(six.u("""Ala ma kota
i zażółca gęślą jaźń
od wieczora do rana."""))

MARKER_CODE = "40g6170ftul9bo17p1r31nqk2a"
XMP = "../../py_mekk_nozbe2xmind/src/mekk/nozbe2xmind/NozbeIconsMarkerPackage.xmp"
root_topic.add_subtopic(six.u("With non-standard marker")).add_marker(MARKER_CODE)

xmind.embed_markers(XMP)

xmind.save(OUTPUT)

#xmind.pretty_print()

print("Saved to", OUTPUT)
