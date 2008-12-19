# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski
#try:
#    from lxml import etree
#except ImportError:
#    from xml.etree import ElementTree as etree
# xml.etree działa ale by szukać z [@x='a'] potrzeba wersji 1.3
from lxml import etree
import zipfile
from id_gen import IdGen, qualify_id, unique_id
from xmlutil import XmlHelper, ns_name, CONTENT_NSMAP, STYLES_NSMAP, find_xpath
import logging
log = logging.getLogger(__name__)

DUMP_PARSED_DATA = False

ATTACHMENTS_DIR = "attachments/"

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

SHAPE_RECTANGLE = "org.xmind.topicShape.rectangle"
SHAPE_ROUND_RECTANGLE = "org.xmind.topicShape.roundedRect"
SHAPE_ELLIPSIS = "org.xmind.topicShape.ellipse"

id_gen = IdGen(26, 16)

class DocumentPart(object):
    def __init__(self, doc):
        self.doc = doc

class Legend(DocumentPart):
    """
    Legenda mapy czyli spis markerów z opisami
    """
    @classmethod
    def create(cls, doc, sheet_tag):
        """
        Tworzy. x_pos i y_pos to pozycje względem centrum mapy
        (ujemne to lewy górny róg, np.)
        """
        legend_tag = doc.create_child(sheet_tag, u"legend", visibility = "visible")
        return Legend(doc, legend_tag)
    def __init__(self, doc, legend_tag):
        DocumentPart.__init__(self, doc)
        self.legend_tag = legend_tag
    def set_position(self, x_pos, y_pos):
        pos = self.doc.find_or_create_child(self.legend_tag, "position")
        pos.set(ns_name("svg", "x"), x_pos)
        pos.set(ns_name("svg", "y"), y_pos)
    def add_marker(self, marker_id, description):
        """
        Dodaje kolejny marker do legendy. marker_id to albo kodowe
        oznaczenie Xmind (priority-1 itp) albo hasz identyfikacyjny
        własnego markera
        """
        md = self.doc.find_or_create_child(self.legend_tag, "marker-descriptions")
        self.doc.create_child(md, u"marker-description",
                              attrib={"marker-id": marker_id,
                                      "description": description})

class Sheet(DocumentPart):
    """
    Reprezentacja strony (tj. diagramu)
    """
    @classmethod
    def create(cls, doc, sheet_name, root_topic_name):
        sheet_tag = doc.create_child(doc.doc_tag, "sheet",
                                     id = id_gen.next())
        sheet = Sheet(doc, sheet_tag)
        sheet.set_title(sheet_name)
        topic_tag = doc.create_child(sheet_tag, u"topic",
                                     id = id_gen.next())
        doc.create_child(topic_tag, u"title").text = root_topic_name
        return sheet

    def __init__(self, doc, sheet_tag):
        DocumentPart.__init__(self, doc)
        self.sheet_tag = sheet_tag

    def set_title(self, title):
        self.doc.find_or_create_child(self.sheet_tag, "title").text = title

    def get_title(self):
        return self.doc.find_only_child(self.sheet_tag, "title").text

    def get_root_topic(self):
        return Topic(self.doc, self.doc.find_only_child(self.sheet_tag, "topic"))

    def get_legend(self):
        l = self.doc.find_only_child(self.sheet_tag, u"legend", required = False)
        if l is not None:
            return Legend(self.doc, l)
        else:
            return Legend.create(self.doc, self.sheet_tag)

class Topic(DocumentPart):
    """
    Reprezentacja pojedynczego tematu (czyli wpisu).
    """
    def __init__(self, doc, topic_tag):
        DocumentPart.__init__(self, doc)
        self.topic_tag = topic_tag

    def get_embedded_id(self):
        """
        Jeśli projekt ma zakopane id, to je zwraca.
        """
        return qualify_id(self.topic_tag.get("id"))

    def get_correlation_id(self):
        """
        Zwraca unikalny identyfikator topicu (w ramach tej mapy)
        """
        return unique_id(self.topic_tag.get("id"))

    def _subtopics_tag(self, detached = False):
        children_tag = self.doc.find_or_create_child(self.topic_tag, "children")
        mode = detached and "detached" or "attached"
        #topics_tag = children_tag.xpath("topics[@type='%s']" % mode)
        #topics_tag[0]
        topics_tag = find_xpath(
            children_tag,
            "%s[@%s='%s']" % (self.doc.xpath_name("topics"),
                              "type", #self.doc.xpath_name("type"),
                              mode),
            single = True, required = False)
        if topics_tag is None:
            topics_tag = self.doc.create_child(children_tag, u"topics", type = mode)
        return topics_tag
    def add_subtopic(self, subtopic_title, subtopic_emb_id = None, detached = False):
        topics_tag = self._subtopics_tag(detached)
        subtopic_tag = self.doc.create_child(topics_tag, u"topic",
                                             id = id_gen.next(subtopic_emb_id))
        self.doc.create_child(subtopic_tag, u"title").text = subtopic_title
        return Topic(self.doc, subtopic_tag)
    def get_subtopics(self, detached = False):
        """
        Generator wyliczający wszystkie pod-elementy. Domyślnie te przypięte, z parametrem
        detached te odpięte.
        """
        topics_tag = self._subtopics_tag(detached)
        for element in self.doc.find_children(topics_tag, "topic"):
            yield Topic(self.doc, element)

    def set_title(self, title):
        self.doc.find_or_create_child(self.topic_tag, "title").text = title
    def get_title(self):
        return self.doc.find_or_create_child(self.topic_tag, "title").text

    def add_marker(self, marker):
        mr = self.doc.find_or_create_child(self.topic_tag, "marker-refs")
        #mr = self.topic_tag.find("marker-refs")
        #if mr is None:
        #    mr = self.doc.create_child(self.topic_tag, "marker-refs")
        self.doc.create_child(mr, "marker-ref", attrib={"marker-id": marker})
    def get_markers(self):
        mr = self.doc.find_only_child(self.topic_tag, "marker-refs", required = False)
        if mr is not None:
            for element in self.doc.find_children(mr, "marker-ref"):
                yield element.get("marker-id")

    def set_link(self, url):
        """
        Dodaje link. Url to np. http://info.onet.pl
        Uwaga: nadpisuje ewentualny istniejący attachment!
        """
        self.topic_tag.set("{http://www.w3.org/1999/xlink}href", url)

    def get_link(self):
        return self.topic_tag.get("{http://www.w3.org/1999/xlink}href")

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
        notes_tag = self.doc.find_or_create_child(self.topic_tag, "notes")
        self.doc.find_or_create_child(notes_tag, "plain").text = note_text
        html_tag = self.doc.find_or_create_child(notes_tag, "html")
        for l in note_text.split("\n"):
            self.doc.create_child(html_tag, "xhtml:p").text = l
    def get_note(self):
        notes_tag = self.doc.find_or_create_child(self.topic_tag, "notes")
        return self.doc.find_or_create_child(notes_tag, "plain").text

    def set_label(self, label_text):
        """
        Ustawia treść etykiety (widocznej krótkiej notki).
        """
        labels_tag = self.doc.find_or_create_child(self.topic_tag, "labels")
        self.doc.find_or_create_child(labels_tag, "label").text = label_text
    def get_label(self):
        labels_tag = self.doc.find_or_create_child(self.topic_tag, "labels")
        return self.doc.find_or_create_child(labels_tag, "label").text

    def set_style(self, style):
        """
        Nadaje notce specyficzny styl. Parametr to TopicStyle
        """
        self.topic_tag.set("style-id", style.get_id())

class TopicStyle(object):
    @classmethod
    def create(cls, doc,
               fill, shape = SHAPE_ROUND_RECTANGLE,
               line_color = "#CACACA", line_width = "1pt"):
        """
        Kolor to np #37D02B
        """
        styles = doc.find_or_create_child(doc.styles_tag, "styles")
        style_tag = doc.create_child(styles, "style",
                                     id = id_gen.next(), type="topic")
        doc.create_child(style_tag, "topic-properties",
                         attrib = {
                             "line-color" : line_color,
                             "line-width" : line_width,
                             "shape-class" : shape,
                             ns_name("svg", "fill") : fill,
                          })
        return TopicStyle(style_tag)
    def __init__(self, style_tag):
        self.style_tag = style_tag
    def get_id(self):
        return self.style_tag.get("id")

class XMindDocument(XmlHelper):
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
        obj = XMindDocument(True, doc_tag, styles_tag)
        obj.create_sheet(first_sheet_name, root_topic_name)
        return obj

    @classmethod
    def open(cls, filename):
        """
        Otwiera istniejący dokument
        """
        zf = zipfile.ZipFile(filename, "r")
        doc_tag = None
        styles_tag = None
        attachments = {}
        for name in zf.namelist():
            if name == "content.xml":
                #doc_tag = etree.parse(zf.open(name), "r")  # python 2.6
                log.debug("parsing content.xml")
                doc_tag = etree.XML(zf.read(name))
            elif name == "styles.xml":
                log.debug("parsing styles.xml")
                styles_tag = etree.XML(zf.read(name))
            elif name in ['meta.xml', 'META-INF/manifest.xml', 'Thumbnails/thumbnail.jpg' ]:
                pass
            elif name.startswith(ATTACHMENTS_DIR):
                short = name[len(ATTACHMENTS_DIR):]
                log.debug("Found attachment %s" % short)
                attachments[short] = zf.read(name)
            elif name.startswith("markers/"):
                pass
            else:
                log.warn("Unknown xmind file member: %s" % name)

        if (doc_tag is None) or (styles_tag is None):
            raise Exception("Invalid xmind file: %s" % filename)

        if DUMP_PARSED_DATA:
            logging.debug("Parsed document:\n%s", etree.tostring(doc_tag, pretty_print = True))
            logging.debug("Parsed styles:\n%s", etree.tostring(styles_tag, pretty_print = True))

        return XMindDocument(False, doc_tag, styles_tag, attachments)

    def __init__(self, is_creating, doc_tag, styles_tag, attachments = {}):
        """
        Wspólny konstruktor. Nie używać bezpośrendnio,
        należy korzystać z metod create albo open.
        """
        XmlHelper.__init__(self, is_creating, "xm")
        #self.is_creating = is_creating
        self.doc_tag = doc_tag
        self.styles_tag = styles_tag
        self.attachments = attachments
        self.embed_xmp = None

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
        sheet_tags = self.find_children(self.doc_tag, "sheet", require_non_empty = True)
        return Sheet(self, sheet_tags[0])

    def embed_markers(self, xmp_file_name):
        """
        Załącza wewnątrz pliku xmnd zbiór scustomizowanych
        markerów. W tym ujęciu są one zadane przez nazwę pliku
        .xmp (czyli eksportu markerów z XMinda).
        
        Można tak zadać tylko jeden plik .xmp, kilkakrotnie
        zawołana funkcja zamienia poprzednie ustawienie.
        
        Uwaga: w bieżącej implementacji zadany plik jest czytany
        w chwili robienia save.
        """
        self.embed_xmp = xmp_file_name

    def save(self, zipfilename):
        zipf = zipfile.ZipFile(zipfilename, "w")
        self._add_to_zip(zipf, "content.xml",
           self._serialize_xml(self.doc_tag))
        self._add_to_zip(zipf, "styles.xml",
           self._serialize_xml(self.styles_tag))
        self._add_to_zip(zipf, "meta.xml", META_FILE_CONTENT)
        manifest_content = MANIFEST_FILE_CONTENT
        for name, data in self.attachments.iteritems():
            path = ATTACHMENTS_DIR + name
            self._add_to_zip(zipf, path, data)
            manifest_content = manifest_content.replace(
                "</manifest>",
                ('<file-entry full-path="%s" media-type=""/>' % path) + "\n</manifest>")
        if self.embed_xmp:
            xmpf = zipfile.ZipFile(self.embed_xmp, "r")
            manifest_content = manifest_content.replace(
                "</manifest>",
                '<file-entry full-path="markers/" media-type=""/>' + "\n</manifest>")
            for name in xmpf.namelist():
                path = "markers/" + name
                self._add_to_zip(
                    zipf, path,
                    xmpf.read(name))
                manifest_content = manifest_content.replace(
                    "</manifest>",
                    ('<file-entry full-path="%s" media-type=""/>' % path) + "\n</manifest>")

        self._add_to_zip(zipf, "META-INF/manifest.xml", manifest_content)

    def pretty_print(self):
        print self._serialize_xml(self.doc_tag)
        print self._serialize_xml(self.styles_tag)

    def attachment_names(self):
        """
        Zwraca listę nazw załączników
        """
        return self.attachments.keys()
    def attachment_body(self, name):
        """
        Zwraca treść załącznika o podanej nazwie
        """
        return self.attachments[name]

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

