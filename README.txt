.. -*- mode: rst; coding: utf-8 -*-

==========
mekk.xmind
==========

``mekk.xmind`` is a pure-Python handler for XMind_ mind-map files.
It can be used to:

- generate XMind_ mind-maps from scratch (for example to visualize
  some data as a mind-map),
- modify existing ``.xmind`` files,
- parse existing ``.xmind`` files and analyze their content.

Examples
========

Creating mind-map::

    from mekk.xmind import XMindDocument
    
    OUTPUT = "test.xmind"
    
    xmind = XMindDocument.create(u"First sheet title", u"Root subject")
    first_sheet = xmind.get_first_sheet()
    root_topic = first_sheet.get_root_topic()
    
    root_topic.add_subtopic(u"First item")
    root_topic.add_subtopic(u"Second item")
    t = root_topic.add_subtopic(u"Third item")
    t.add_subtopic(u"Second level - 1")
    t.add_subtopic(u"Second level - 2")
    root_topic.add_subtopic(u"Detached topic", detached = True)
    t.add_subtopic(u"Another detached", detached = True)
    t.add_marker("flag-red")
    root_topic.add_subtopic(u"Link example").set_link("http://mekk.waw.pl")
    root_topic.add_subtopic(u"Attachment example").set_attachment(
        file("map_creator.py").read(), ".txt")
    root_topic.add_subtopic(u"With note").set_note(u"""This is just some
dummy note.""")
    
    MARKER_CODE = "40g6170ftul9bo17p1r31nqk2a"
    XMP = "../../py_mekk_nozbe2xmind/src/mekk/nozbe2xmind/NozbeIconsMarkerPackage.xmp"
    root_topic.add_subtopic(u"With non-standard marker").add_marker(MARKER_CODE)
    
    xmind.embed_markers(XMP)
    
    xmind.save(OUTPUT)
    
    #xmind.pretty_print()
    
    print "Saved to", OUTPUT

Note: while examples above use ascii, unicode is fully supported.

Parsing mind map::

    from mekk.xmind import XMindDocument
    
    xmind = XMindDocument.open("test.xmind")
    
    sheet = xmind.get_first_sheet()
    print "Sheet title: ", sheet.get_title()
    
    root = sheet.get_root_topic()
    print "Root title: ", root.get_title()
    print "Root note: ", root.get_note()
    
    for topic in root.get_subtopics():
        print "* ", topic.get_title()
        print "   label: ", topic.get_label()
        print "   link: ", topic.get_link()
        print "   markers: ", list(topic.get_markers())
        # topic.get_subtopics()
    
etc.

To modify, just parse existing document, find items to modify and
change them as appropriate, then save.

Development
===========

The code is tracked using Mercurial. Repository can be found on
http://bitbucket.org/Mekk/mekk.xmind/.

Use the same place to report bugs, suggest improvements and offer
patches.

.. _XMind: http://xmind.net
