# -*- coding: utf-8 -*-
#try:
#    from lxml import etree
#except ImportError:
#    from xml.etree import ElementTree as etree
# xml.etree działa ale by szukać z [@x='a'] potrzeba wersji 1.3
from lxml import etree
import zipfile
from id_gen import IdGen

# Na windows działa easy_install lxml==2.1.3
# (ogólnie jakaś wersja co ma buidl win)

CONTENT_NSMAP = {
    None : "urn:xmind:xmap:xmlns:content:2.0",
    "fo" : "http://www.w3.org/1999/XSL/Format",
    "svg" : "http://www.w3.org/2000/svg",
    "xhtml" : "http://www.w3.org/1999/xhtml",
    "xlink" : "http://www.w3.org/1999/xlink",
}

def content_name(ns, what):
    """
    Generuje nazwę zawierającą namespace, np.

    >>> content_name("svg", "x")
    "{http://www.w3.org/2000/svg}x"
    """
    return "{%s}%s" % (CONTENT_NSMAP[ns], what)

STYLES_NSMAP = {
    None : "urn:xmind:xmap:xmlns:style:2.0",
    "fo" : "http://www.w3.org/1999/XSL/Format",
    "svg" : "http://www.w3.org/2000/svg",
}

META_FILE_CONTENT = u'<?xml version="1.0" encoding="UTF-8" standalone="no"?><meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"/>'
MANIFEST_FILE_CONTENT = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/" media-type=""/>
  <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
  <file-entry full-path="styles.xml" media-type=""/>
  <file-entry full-path="Thumbnails/" media-type=""/>
  <file-entry full-path="Thumbnails/thumbnail.jpg" media-type="image/jpeg"/>
</manifest>'''

# Patrz org.xmind.ui.resources/markers/markerSheet.xml
ALL_MARKS = [
    'priority-1', 'priority-2', 'priority-3', 'priority-4', 'priority-5', 'priority-6',
    'flag-red', 'flag-orange', 'flag-green', 'flag-purple', 'flag-blue', 'flag-black',
    'smiley-smile', 'smiley-laugh', 'smiley-angry', 'smiley-cry', 'smiley-surprise', 'smiley-boring',
    'other-calendar', 'other-email', 'other-phone', 'other-fax', 'other-people',
    'other-clock', 'other-coffee-cup', 'other-question', 'other-exclam', 'other-lightbulb',
    'task-start', 'task-quarter', 'task-half', 'task-3quar', 'task-done', 'task-pause',
]

id_gen = IdGen(26, 16)

def find_or_create_tag(parent, tag_name):
    """
    If parent contains tag tag_name, returns its obj.
    Otherwise creates one and returns.
    """
    child = parent.find(tag_name)
    if child is None:
        child = etree.SubElement(parent, tag_name)
    return child

def find_tag(parent, tag_name):
    child = parent.find(tag_name)
    if child is None:
        raise Exception("Tag %(tag_name)s not found" % locals())
    return child

class Legend(object):
    """
    Legenda mapy czyli spis markerów z opisami
    """
    @classmethod
    def create(cls, sheet_tag):
        """
        Tworzy. x_pos i y_pos to pozycje względem centrum mapy
        (ujemne to lewy górny róg, np.)
        """
        legend_tag = etree.SubElement(sheet_tag, u"legend", visibility = "visible")
        return Legend(legend_tag)
    def __init__(self, legend_tag):
        self.legend_tag = legend_tag
    def set_position(self, x_pos, y_pos):
        pos = find_or_create_tag(self.legend_tag, "position")
        pos.set(content_nsmap("svg", "x"), x_pos)
        pos.set(content_nsmap("svg", "y"), y_pos)
    def add_marker(self, marker_id, description):
        """
        Dodaje kolejny marker do legendy. marker_id to albo kodowe
        oznaczenie Xmind (priority-1 itp) albo hasz identyfikacyjny
        własnego markera
        """
        md = find_or_create_tag(self.legend_tag, "marker-descriptions")
        etree.SubElement(md, u"marker-description",
                         attrib={"marker-id": marker_id,
                                 "description": description})

class Sheet(object):
    """
    Reprezentacja strony (tj. diagramu)
    """
    @classmethod
    def create(cls, doc, sheet_name, root_topic_name):
        sheet_tag = etree.SubElement(doc.doc_tag, "sheet",
                                     id = id_gen.next())
        sheet = Sheet(sheet_tag, doc)
        sheet.set_title(sheet_name)
        topic_tag = etree.SubElement(sheet_tag, u"topic",
                                     id = id_gen.next())
        etree.SubElement(topic_tag, u"title").text = root_topic_name
        return sheet

    def __init__(self, sheet_tag, doc):
        self.sheet_tag = sheet_tag
        self.doc = doc

    def set_title(self, title):
        find_or_create_tag(self.sheet_tag, "title").text = title

    def get_root_topic(self):
        return Topic(find_tag(self.sheet_tag, "topic"), self.doc)

    def get_legend(self):
        l = self.sheet_tag.find("legend")
        if l:
            return Legend(l)
        else:
            return Legend.create(self.sheet_tag)

class Topic(object):
    """
    Reprezentacja pojedynczego tematu (czyli wpisu).
    """
    def __init__(self, topic_tag, doc):
        self.topic_tag = topic_tag
        self.doc = doc
    def add_subtopic(self, subtopic_title, subtopic_emb_id = None, detached = False):
        children_tag = find_or_create_tag(self.topic_tag, "children")
        mode = detached and "detached" or "attached"
        #topics_tag = children_tag.xpath("topics[@type='%s']" % mode)
        #topics_tag[0]
        topics_tag = children_tag.find("topics[@type='%s']" % mode)
        if topics_tag is None:
            topics_tag = etree.SubElement(children_tag, u"topics", type = mode)
        subtopic_tag = etree.SubElement(topics_tag, u"topic",
                                        id = id_gen.next(subtopic_emb_id))
        etree.SubElement(subtopic_tag, u"title").text = subtopic_title
        return Topic(subtopic_tag, self.doc)

    def set_title(self, title):
        find_or_create_tag(self.topic_tag, "title").text = title

    def add_marker(self, marker):
        mr = self.topic_tag.find("marker-refs")
        if mr is None:
            mr = etree.SubElement(self.topic_tag, "marker-refs")
        etree.SubElement(mr, "marker-ref", attrib={"marker-id": marker})

    def set_link(self, url):
        """
        Dodaje link. Url to np. http://info.onet.pl
        Uwaga: nadpisuje ewentualny istniejący attachment!
        """
        self.topic_tag.set("{http://www.w3.org/1999/xlink}href", url)

    def set_attachment(self, data, extension):
        """
        Dodaje załącznik (wpisuje go do pliku i dowiązuje w tym topicu).
        Uwaga: nadmazuje ewentualny link.

        @param data dane (po prostu treść pliku do wpisania)
        @param extension (rozszerzenie nazwy pliku, np. '.txt')
        """
        att_name = id_gen.next() + extension
        self.doc._create_attachment(att_name, data)
        self.topic_tag.set("{http://www.w3.org/1999/xlink}href", "xap:attachments/" + att_name)

    def set_note(self, note_text):
        """
        Ustawia treść notki. Tekst może być wielowierszowy.
        """
        # TODO: obsługa HTML
        notes_tag = find_or_create_tag(self.topic_tag, "notes")
        find_or_create_tag(notes_tag, "plain").text = note_text
        html_tag = find_or_create_tag(notes_tag, "html")
        for l in note_text.split("\n"):
            etree.SubElement(html_tag, "{http://www.w3.org/1999/xhtml}p").text = l

    def set_style(self, style):
        """
        Nadaje notce specyficzny styl. Parametr to TopicStyle
        """
        self.topic_tag.set("style-id", style.get_id())

class TopicStyle(object):
    @classmethod
    def create(cls, doc,
               fill, shape = "org.xmind.topicShape.ellipse",
               line_color = "#CACACA", line_width = "1pt"):
        """
        Kolor to np #37D02B
        """
        styles = find_or_create_tag(doc.styles_tag, "styles")
        style_tag = etree.SubElement(styles, "style",
                                     id = id_gen.next(), type="topic")
        etree.SubElement(style_tag, "topic-properties",
                         attrib = {
                                   "line-color" : line_color,
                                   "line-width" : line_width,
                                   "shape-class" : shape,
                                   content_name("svg", "fill") : fill,
                                   })
        return TopicStyle(style_tag)
    def __init__(self, style_tag):
        self.style_tag = style_tag
    def get_id(self):
        return self.style_tag.get("id")

class XMindDocument(object):
    """
    Reprezentacja obiektu dokumentu XMinda. Służy zarówno do tworzenia nowych
    dokumentów, jak do analizy istniejących.
    """

    @classmethod
    def create(cls, first_sheet_name, root_topic_name):
        """
        Tworzy nowy, pusty dokument
        """
        doc_tag = etree.Element("xmap-content", nsmap = CONTENT_NSMAP, version = "2.0")
        styles_tag = etree.Element("xmap-styles", nsmap = STYLES_NSMAP, version = "2.0")
        obj = XMindDocument(doc_tag, styles_tag)
        obj.create_sheet(first_sheet_name, root_topic_name)
        return obj

    @classmethod
    def open(cls, filename):
        """
        Otwiera istniejący dokument
        """
        # TODO: otworzyć zipa, zapisać listę attachmentów, sparsować style
        # oraz główny content
        raise NotImplementedError
        xml = etree.parse(file(filename, "r"))
        return XMindDocument(xml)

    def __init__(self, doc_tag, styles_tag, attachments = None):
        """
        Wspólny konstruktor. Nie używać bezpośrendnio,
        należy korzystać z metod create albo open.
        """
        self.doc_tag = doc_tag
        self.styles_tag = styles_tag
        self.attachments = {}

    def create_sheet(self, sheet_name, root_topic_name):
        sheet = Sheet.create(self,
                             sheet_name, root_topic_name)
        return sheet

    def create_topic_style(self, *args, **kwargs):
        """
        Wrapper dookoła TopicStyle.create. Te same parametry
        """
        return TopicStyle.create(self, *args, **kwargs)

    def get_first_sheet(self):
        tag = find_tag(self.doc_tag, "sheet")
        return Sheet(tag, self)

    def save(self, zipfilename):
        zipf = zipfile.ZipFile(zipfilename, "w")
        self._add_to_zip(zipf, "content.xml",
           self._serialize_xml(self.doc_tag))
        self._add_to_zip(zipf, "styles.xml",
           self._serialize_xml(self.styles_tag))
        self._add_to_zip(zipf, "meta.xml", META_FILE_CONTENT)
        manifest_content = MANIFEST_FILE_CONTENT
        for name, data in self.attachments.iteritems():
            path = "attachments/" + name
            self._add_to_zip(zipf, path, data)
            manifest_content = manifest_content.replace(
                "</manifest>",
                ('<file-entry full-path="%s" media-type=""/>' % path) + "\n</manifest>")
        self._add_to_zip(zipf, "META-INF/manifest.xml", manifest_content)

    def pretty_print(self):
        print self._serialize_xml(self.doc_tag)
        print self._serialize_xml(self.styles_tag)

    def _create_attachment(self, internal_name, data):
        """
        Nie używać! Używać metody set_attachment klasy Topic
        """
        self.attachments[internal_name] = data

    def _add_to_zip(self, zipf, name, content):
        if type(content) == unicode:
            content = content.encode("utf-8")
        zipf.writestr(name, content)
    def _serialize_xml(self, tag):
        return etree.tostring(
            tag,
            encoding = "utf-8", method="xml",
            xml_declaration=True, pretty_print=True,
            with_tail=True)

# TODO: obsługa styli
#
# <xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" version="2.0">
# <styles>
#    <style id="3hj12gila7eq1otcid1q9tn7ji" type="text">
#      <text-properties fo:color="#000000"/>
#    </style>
#    <style id="1402637o7i7qq98bb5uthrmtap" type="topic">
#      <topic-properties shape-class="org.xmind.topicShape.callout.ellipse"/>
#    </style>
#  </styles>
#</xmap-styles>
