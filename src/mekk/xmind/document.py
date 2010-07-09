# -*- coding: utf-8 -*-
# (c) 2008-2010, Marcin Kasperski

"""
Create and parse XMind maps.
"""

from lxml import etree
import zipfile
from id_gen import IdGen, qualify_id, unique_id
from xmlutil import XmlHelper, ns_name, \
    CONTENT_NSMAP, STYLES_NSMAP, find_xpath
import logging

log = logging.getLogger(__name__)

DUMP_PARSED_DATA = False

ATTACHMENTS_DIR = "attachments/"

META_FILE_BODY = u'<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + \
    '<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"/>'
MANIFEST_FILE_BODY = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/" media-type=""/>
  <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
  <file-entry full-path="styles.xml" media-type=""/>
  <file-entry full-path="Thumbnails/" media-type=""/>
  <file-entry full-path="Thumbnails/thumbnail.jpg" media-type="image/jpeg"/>
</manifest>'''

# See org.xmind.ui.resources/markers/markerSheet.xml
ALL_MARKS = [
    'priority-1', 'priority-2', 'priority-3',
    'priority-4', 'priority-5', 'priority-6',
    'flag-red', 'flag-orange', 'flag-green',
    'flag-purple', 'flag-blue', 'flag-black',
    'smiley-smile', 'smiley-laugh', 'smiley-angry',
    'smiley-cry', 'smiley-surprise', 'smiley-boring',
    'other-calendar', 'other-email', 'other-phone', 'other-fax',
    'other-people', 'other-clock', 'other-coffee-cup', 'other-question',
    'other-exclam', 'other-lightbulb',
    'task-start', 'task-quarter', 'task-half',
    'task-3quar', 'task-done', 'task-pause',
]

SHAPE_RECTANGLE = "org.xmind.topicShape.rectangle"
SHAPE_ROUND_RECTANGLE = "org.xmind.topicShape.roundedRect"
SHAPE_ELLIPSIS = "org.xmind.topicShape.ellipse"

_id_gen = IdGen(26)

class DocumentPart(object):
    """
    Base class for all mindmap related objects (sheets, topics, legends etc).
    Provides .doc attribute
    """

    def __init__(self, doc):
        self.doc = doc

class Legend(DocumentPart):
    """
    Map legend handling.

    Legend can be used to describe meaning of markers (graphical
    symbols) present on the map, is displayed as a rectangular box
    containing markers and their descriptions. By default it is empty,
    markers which are to be described should be added using ``add_marker``
    method.

    Legend object is usually created/accessed via Sheet.get_legend.

    >>> legend = sheet.get_legend()
    >>> legend.add_marker(
    ...     "task-done", u"Task done")
    >>> legend.add_marker(
    ...     "task-start", u"Task being worked on")
    """
    @classmethod
    def create(cls, doc, sheet_tag):
        """
        Creates legend on the mind-map. Usually not
        used directly (see Sheet.get_legend instead).

        Arguments
        ---------

        doc : XMindDocument
            MindMap being modified
        sheet_tag : etree
            XML node of <sheet>
        """
        legend_tag = doc.create_child(
            sheet_tag, u"legend", visibility = "visible")
        return Legend(doc, legend_tag)

    def __init__(self, doc, legend_tag):
        DocumentPart.__init__(self, doc)
        self.legend_tag = legend_tag

    def set_position(self, x_pos, y_pos):
        """
        Enforce legend position on the sheet.

        >>> sheet.get_legend().set_position(500, 500)

        Arguments
        ---------

        x_pos : int
            Horizontal position (in pixels, 0 means left border)
        y_pos : int
            Vertical position (in pixels, 0 means top border)
        """
        pos = self.doc.find_or_create_child(self.legend_tag, "position")
        pos.set(ns_name("svg", "x"), x_pos)
        pos.set(ns_name("svg", "y"), y_pos)

    def add_marker(self, marker_id, description):
        """
        Adds marker to the legend with given description.

        >>> sheet.get_legend().add_marker(
        ...     "task-done", u"Task done")

        Arguments
        ---------

        marker_id : string
             Either name of one of the prederined XMind markers
             (one of the constants in ALL_MARKS), or hashed string
             which identifies custom marker from embedded markers
             (see XMindDocument.embed_markers)
        description : string
             Short marker description to be put on the legend.
        """
        markers_block = self.doc.find_or_create_child(
            self.legend_tag, "marker-descriptions")
        self.doc.create_child(markers_block, u"marker-description",
                              attrib={"marker-id": marker_id,
                                      "description": description})

class Sheet(DocumentPart):
    """
    Represents single sheet (diagram) on the mind-map
    (note that XMind handles many sheet per diagram).
    """
    @classmethod
    def create(cls, doc, sheet_name, root_topic_name):
        """
        Create new sheet. Usually not used directly,
        use ``XMindDocument.create_sheet`` instead.
        """
        sheet_tag = doc.create_child(doc.doc_tag, "sheet",
                                     id = _id_gen.next())
        sheet = Sheet(doc, sheet_tag)
        sheet.set_title(sheet_name)
        topic_tag = doc.create_child(sheet_tag, u"topic",
                                     id = _id_gen.next())
        doc.create_child(topic_tag, u"title").text = root_topic_name
        return sheet

    def __init__(self, doc, sheet_tag):
        DocumentPart.__init__(self, doc)
        self.sheet_tag = sheet_tag

    def set_title(self, title):
        """
        Change sheet title (label displayed on sheet tab).
        """
        self.doc.find_or_create_child(self.sheet_tag, "title").text = title

    def get_title(self):
        """
        Get the sheet title
        """
        return self.doc.find_only_child(self.sheet_tag, "title").text

    def get_root_topic(self):
        """
        Get the root topic of the sheet (this topic always exists)
        """
        return Topic(self.doc, self.doc.find_only_child(
                self.sheet_tag, "topic"))

    def get_legend(self):
        """
        Get the legend object for the sheet, create it if it does
        not exist.
        """
        legend_tag = self.doc.find_only_child(
            self.sheet_tag, u"legend", required = False)
        if legend_tag is not None:
            return Legend(self.doc, legend_tag)
        else:
            return Legend.create(self.doc, self.sheet_tag)

class Topic(DocumentPart):
    """
    Representation of single topic (item) on the map.
    """
    def __init__(self, doc, topic_tag):
        DocumentPart.__init__(self, doc)
        self.topic_tag = topic_tag

    def get_embedded_id(self):
        """
        Read and return so called "embedded topic id", if present,
        otherwise returns None.

        "embedded ids" are purely mekk.xmind convention used to
        identify topics in scenarios where some map is created with
        mekk.xmind, then edited inside XMind, then parsed again with
        mekk.xmind. As XMind identifies every topic on the map with a
        identifier (and preserves this identifier while the topic is
        edited), mekk.xmind just uses this field, adding some specific
        prefix to detect new topics.

        So, using get_embedded_id makes sense only on maps which
        were initially created with mekk.xmind. If such an id is specified
        while topic is created, then it can be recognized after map is edited.

        The method returns None for topics created directly
        inside XMind.
        """
        return qualify_id(self.topic_tag.get("id"))

    def get_correlation_id(self):
        """
        Returns unique identifier for given topic. The identifier
        is unique within the whole map and is never empty, can be
        used - for example - as a key in structures containing topics.
        """
        return unique_id(self.topic_tag.get("id"))

    def _subtopics_tag(self, detached = False):
        """
        Internal helper. Returns XML tag for subtopics block
        """
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
            topics_tag = self.doc.create_child(
                children_tag, u"topics", type = mode)
        return topics_tag

    def add_subtopic(self, subtopic_title, 
                     subtopic_emb_id = None, detached = False):
        """
        Create new topic as a child of this topic.

        Arguments
        ---------

        subtopic_title : unicode
            Title (label) of newly added topic
        subtopic_emb_id : string (optional)
            Embedded identifier (see comment for `get_embedded_id`)
        detached : bool (default False)
            Make subtopic detached (not connected to the parent).
            Usually used only while adding child to the root topic,
            but seems to work elsewhere too.
        """
        topics_tag = self._subtopics_tag(detached)
        subtopic_tag = self.doc.create_child(topics_tag, u"topic",
                                             id = _id_gen.next(subtopic_emb_id))
        self.doc.create_child(subtopic_tag, u"title").text = subtopic_title
        return Topic(self.doc, subtopic_tag)

    def get_subtopics(self, detached = False):
        """
        Yields all subtopics of this topic. By default
        connected children are returned, if `detached` param
        is set, disconnected (detached) chilren are returned.
        """
        topics_tag = self._subtopics_tag(detached)
        for element in self.doc.find_children(topics_tag, "topic"):
            yield Topic(self.doc, element)

    def set_title(self, title):
        """
        Change topic title
        """
        self.doc.find_or_create_child(self.topic_tag, "title").text = title

    def get_title(self):
        """
        Returns topic title
        """
        return self.doc.find_or_create_child(self.topic_tag, "title").text

    def add_marker(self, marker):
        """
        Add graphical marker to the topic.

        Note: single topic can have many markers (but it is not very
        pleasant visually).

        Arguments
        ---------

        marker : string
             Either name of one of the prederined XMind markers
             (one of the constants in `ALL_MARKS`), or hashed string
             which identifies custom marker from embedded markers
             (see XMindDocument.embed_markers)
        """
        marker_refs_tag = self.doc.find_or_create_child(
            self.topic_tag, "marker-refs")
        self.doc.create_child(
            marker_refs_tag, "marker-ref", attrib={"marker-id": marker})

    def get_markers(self):
        """
        Yields all markers currently attached to the topic.
        Returned values have semantics described in ``add_marker``
        (are either predefined constants like ``smiley-laugh``,
        or hashed identifiers for attached marker sheet items).
        """
        marker_refs_tag = self.doc.find_only_child(
            self.topic_tag, "marker-refs", required = False)
        if marker_refs_tag is not None:
            for element in self.doc.find_children(
                    marker_refs_tag, "marker-ref"):
                yield element.get("marker-id")

    def set_link(self, url):
        """
        Adds/replaces http(s) link to the topic. XMind will show
        that the link is present and will make it possible to open
        linked page using external or internal web browser.

        Warning: setting link removes attachment, if present, topic
        can't contain both.

        Arguments
        ----------

        url : string
            Page address (for example "http://slashdot.org")
        """
        self.topic_tag.set("{http://www.w3.org/1999/xlink}href", url)

    def get_link(self):
        """
        Returns link (url) attached to topic, if present, or None, if not.
        """
        return self.topic_tag.get("{http://www.w3.org/1999/xlink}href")

    def set_attachment(self, data, extension):
        """
        Attaches some data to the topic. Given data are saved inside
        generated mind map, and linked to this topic.

        Warning: setting attachment removes any previous attachment
        and also any set link.

        Arguments
        ---------

        data : string
             actual data (usually content of some file)
        extension : string
             file extension (used to signal the data format, for example
             ``.txt``, ``.html``, ``.zip``, ``.json``)
        """
        att_name = _id_gen.next() + extension
        self.doc._create_attachment(att_name, data)
        self.topic_tag.set("{http://www.w3.org/1999/xlink}href",
                           "xap:attachments/" + att_name)

    def set_note(self, note_text):
        """
        Adds/replaces topic note (long text attached to the topic).

        Line breaks are preserved (to mark paragraphs), apart from that
        no formatting is handled.
        """
        notes_tag = self.doc.find_or_create_child(self.topic_tag, "notes")
        self.doc.find_or_create_child(notes_tag, "plain").text = note_text
        html_tag = self.doc.find_or_create_child(notes_tag, "html")
        for line in note_text.split("\n"):
            self.doc.create_child(html_tag, "xhtml:p").text = line

    # TODO: Implement set_note_html(self, html_text). Difficulty: HTML tags
    # must be namespace prefixed.

    def get_note(self):
        """
        Returns note (topic description) text, or empty string
        if it is not present
        """
        notes_tag = self.doc.find_or_create_child(self.topic_tag, "notes")
        return self.doc.find_or_create_child(notes_tag, "plain").text

    def set_label(self, label_text):
        """
        Sets/replaces topic label (short tag-like annotation)
        """
        labels_tag = self.doc.find_or_create_child(self.topic_tag, "labels")
        self.doc.find_or_create_child(labels_tag, "label").text = label_text

    def get_label(self):
        """
        Gets topic label (or empty text if missing)
        """
        labels_tag = self.doc.find_or_create_child(self.topic_tag, "labels")
        return self.doc.find_or_create_child(labels_tag, "label").text

    def set_style(self, style):
        """
        Attaches specific visual style to the topic.

        Arguments
        ---------

        style : TopicStyle
            Object defining visual characteristics of the topic
            (usually created via XMindDocument.create_topic_style)
        """
        self.topic_tag.set("style-id", style.get_id())

class TopicStyle(object):
    """
    Topic visual presentation style. To be used as Topic.set_style
    parameter.

    Single TopicStyle can be used for many topics.
    """

    @classmethod
    def create(cls, doc,
               fill, shape = SHAPE_ROUND_RECTANGLE,
               line_color = "#CACACA", line_width = "1pt"):
        """
        Create style object, saving it inside the map. Such
        object can be later attached to topics using set_style.

        Note: while this method can be used directly, the recommended
        way is to call XMindDocument.create_topic_style(...)

        Arguments
        ---------

        doc : XMindDocument
            Map object (style is always
        fill : string
            Background color (using SVG notation, for example
            ``#37D02B``)
        shape : string (optional)
            Shape (SHAPE_RECTANGLE, SHNAPE_ROUND_RECTANGLE or SHAPE_ELLIPSIS)
        line_color : string (optional)
            Border color (SVG, for example ``#AABBCC``)
        line_width : string (optional)
            Border width (SVG-like, for example ``1pt``)
        """
        styles = doc.find_or_create_child(doc.styles_tag, "styles")
        style_tag = doc.create_child(styles, "style",
                                     id = _id_gen.next(), type="topic")
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
        """
        Returns internal object identifier (unique within map)
        """
        return self.style_tag.get("id")

class XMindDocument(XmlHelper):
    """
    Whole XMind document representation
    """

    @classmethod
    def create(cls, first_sheet_name, root_topic_name):
        """
        Create new, almost empty document, with just one
        sheet and it's root topic. Document can be manipulated
        using library API (usually via sheets), then saved using ``save``.
        """
        doc_tag = etree.Element(
            "xmap-content", nsmap = CONTENT_NSMAP, version = "2.0")
        styles_tag = etree.Element(
            "xmap-styles", nsmap = STYLES_NSMAP, version = "2.0")
        obj = XMindDocument(True, doc_tag, styles_tag)
        obj.create_sheet(first_sheet_name, root_topic_name)
        return obj

    @classmethod
    def open(cls, filename):
        """
        Open and parse existing mind-map.
        """
        archive = zipfile.ZipFile(filename, "r")
        doc_tag = None
        styles_tag = None
        attachments = {}
        for name in archive.namelist():
            if name == "content.xml":
                #doc_tag = etree.parse(archive.open(name), "r")  # python 2.6
                log.debug("parsing content.xml")
                doc_tag = etree.XML(archive.read(name))
            elif name == "styles.xml":
                log.debug("parsing styles.xml")
                styles_tag = etree.XML(archive.read(name))
            elif name in ['meta.xml', 'META-INF/manifest.xml',
                          'Thumbnails/thumbnail.jpg' ]:
                pass
            elif name.startswith(ATTACHMENTS_DIR):
                short = name[len(ATTACHMENTS_DIR):]
                log.debug("Found attachment %s" % short)
                attachments[short] = archive.read(name)
            elif name.startswith("markers/"):
                pass
            else:
                log.warn("Unknown xmind file member: %s" % name)

        if doc_tag is None:
            raise Exception("Invalid xmind file: %s (missing content block)" % filename)
        if styles_tag is None:
            #  XMind 3.1.1 happens to miss this tag
            #raise Exception("Invalid xmind file: %s (missing style block)" % filename)
            styles_tag = etree.Element(
                "xmap-styles", nsmap = STYLES_NSMAP, version = "2.0")

        if DUMP_PARSED_DATA:
            logging.debug("Parsed document:\n%s",
                          etree.tostring(doc_tag, pretty_print = True))
            logging.debug("Parsed styles:\n%s",
                          etree.tostring(styles_tag, pretty_print = True))

        return XMindDocument(False, doc_tag, styles_tag, attachments)

    def __init__(self, is_creating, doc_tag, styles_tag, attachments = None):
        """
        Constructor. Don't use directly, use
        XMindDocument.create or XMindDocument.open
        """
        XmlHelper.__init__(self, is_creating, "xm")
        self.doc_tag = doc_tag
        self.styles_tag = styles_tag
        self.attachments = (attachments or {})
        self.embed_xmp = None

    def create_sheet(self, sheet_name, root_topic_name):
        """
        Add new sheet (and return it)
        """
        sheet = Sheet.create(self,
                             sheet_name, root_topic_name)
        return sheet

    def create_topic_style(self, *args, **kwargs):
        """
        Create visual topic style (which can be attached
        to one or more topics with topic.set_style(style).

        The parameters are identical as in TopicStyle.create
        (except doc).
        """
        return TopicStyle.create(self, *args, **kwargs)

    def get_first_sheet(self):
        """
        Return first sheet of the map.
        """
        sheet_tags = self.find_children(
            self.doc_tag, "sheet", require_non_empty = True)
        return Sheet(self, sheet_tags[0])

    def get_all_sheets(self):
        """
        Yields all sheets of the map.
        """
        sheet_tags = self.find_children(
            self.doc_tag, "sheet", require_non_empty = True)
        for sheet_tag in sheet_tags:
            yield Sheet(self, sheet_tag)

    def embed_markers(self, xmp_file_name):
        """
        Attaches to the map set of custom markers (graphical icons
        used to mark topics). Markers will be saved inside the map,
        so will be visible on other installations.

        Only one marker set can be embedded, successive calls
        to this function overwrite previous values.

        Arguments
        ---------

        xmp_file_name : string (file name)
            Name of ``.xmp`` file to be embedded.
            The best way to create such a file is to export
            markers using appropriate XMind option.

        Note: the file is not immediately accessed, it's content
        is copied during ``save``.
        """
        self.embed_xmp = xmp_file_name

    def save(self, output_file_name):
        """
        Save mindmap to given file.
        """
        zipf = zipfile.ZipFile(output_file_name, "w")
        self._add_to_zip(zipf, "content.xml",
           self._serialize_xml(self.doc_tag))
        self._add_to_zip(zipf, "styles.xml",
           self._serialize_xml(self.styles_tag))
        self._add_to_zip(zipf, "meta.xml", META_FILE_BODY)
        manifest_content = MANIFEST_FILE_BODY
        for name, data in self.attachments.iteritems():
            path = ATTACHMENTS_DIR + name
            self._add_to_zip(zipf, path, data)
            manifest_content = manifest_content.replace(
                "</manifest>",
                ('<file-entry full-path="%s" media-type=""/>' % path)
                + "\n</manifest>")
        if self.embed_xmp:
            xmpf = zipfile.ZipFile(self.embed_xmp, "r")
            manifest_content = manifest_content.replace(
                "</manifest>",
                '<file-entry full-path="markers/" media-type=""/>'
                + "\n</manifest>")
            for name in xmpf.namelist():
                path = "markers/" + name
                self._add_to_zip(
                    zipf, path,
                    xmpf.read(name))
                manifest_content = manifest_content.replace(
                    "</manifest>",
                    ('<file-entry full-path="%s" media-type=""/>' % path)
                    + "\n</manifest>")

        self._add_to_zip(zipf, "META-INF/manifest.xml", manifest_content)

    def pretty_print(self):
        """
        Debug helper, prints internal map structure to the screen
        """
        print self._serialize_xml(self.doc_tag)
        print self._serialize_xml(self.styles_tag)

    def attachment_names(self):
        """
        Return names of all attachments present inside the map
        (independent to which topic they are attached).
        """
        return self.attachments.keys()

    def attachment_body(self, name):
        """
        Returns body of attachment of given name.
        """
        return self.attachments[name]

    def _create_attachment(self, internal_name, data):
        """
        Private attachment-creation helper.
        Use Topic.set_attachment instead!
        """
        self.attachments[internal_name] = data

    def _add_to_zip(self, zipf, name, content):
        """
        Add member of name name and content content to zipfile zipf.
        """
        if type(content) == unicode:
            content = content.encode("utf-8")
        zipf.writestr(name, content)

    def _serialize_xml(self, tag):
        """
        Serialize given tag to text using proper settings.
        """
        return etree.tostring(
            tag,
            encoding = "utf-8", method="xml",
            xml_declaration=True, pretty_print=True,
            with_tail=True)

