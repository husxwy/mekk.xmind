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
