# -*- coding: utf-8 -*-
# (c) 2008-2010, Marcin Kasperski

"""
Set of helpers and constants used while generating and parsing
XMind XML.
"""

# Note:
#
# While creating map non-prefixed (non-namespaced) tags are used
# and they work. Unforutnately while parsing it is necessary
# to prefix tags searched for. Bad luck.

# TODO: think about    //*[local-name()='bar']

from lxml import etree

class InternalStructureException(Exception):
    """
    Exception thrown in case of missing children, unexpected
    children and other internal XML structure errors.
    """
    def __init__(self, text):
        Exception.__init__(self)
        self.text = text
    def __str__(self):
        return "Internal map processing error (%s)" % self.text

NS_CONTENT = "urn:xmind:xmap:xmlns:content:2.0"
NS_STYLE = "urn:xmind:xmap:xmlns:style:2.0"
NS_FO = "http://www.w3.org/1999/XSL/Format"
NS_SVG = "http://www.w3.org/2000/svg"
NS_XHTML = "http://www.w3.org/1999/xhtml"
NS_XLINK = "http://www.w3.org/1999/xlink"

STYLES_NSMAP = {
    None : NS_STYLE,
    "fo" : NS_FO,
    "svg" : NS_SVG,
}
CONTENT_NSMAP = {
    None : NS_CONTENT,
    "fo" : NS_FO,
    "svg" : NS_SVG,
    "xhtml" : NS_XHTML,
    "xlink" : NS_XLINK,
}
SEARCH_NSMAP = {
    "xm" : NS_CONTENT,
    "st" : NS_STYLE,
    "svg" : NS_SVG,
    "xhtml" : NS_XHTML,
    "fo" : NS_FO,
    "xlink" : NS_XLINK,
}

########################################################################
# Ogólne
########################################################################

def ns_name(ns_shortcut, what):
    """
    Make properly namespace-prefixed tag name, for example:

    >>> ns_name("svg", "x")
    "{http://www.w3.org/2000/svg}x"
    """
    return "{%s}%s" % (SEARCH_NSMAP[ns_shortcut], what)

def find_xpath(parent, expression, single = False, required = False):
    """
    Look inside parent for elements satisfying XPath expression, returns
    the results. Handles namespace shortcuts (xm:topic, svg:color etc)

    If single is set, expects no more than one result (otherwise raises
    InternalStructureException), and returns scalar value (or None if nothing is found).
    With single not set, returns list.

    If required is set, raises InternalStructureException if nothing is found.
    """
    found_items = parent.xpath(expression, namespaces = SEARCH_NSMAP)
    if required and (not found_items):
        raise InternalStructureException(
            "Bad structure. Element %s not found under %s" % (
                expression, parent))
    if single:
        if len(found_items) > 1:
            raise InternalStructureException(
                "Non-unique child %s under parent %s" % (
                    expression, parent))
        elif found_items:
            found_items = found_items[0]
        else:
            found_items = None
    return found_items

############################################################################3
# Kontekstowe
############################################################################3

def _optional_ns_fullname(name):
    """
    If name contains colon, performs ns_name on it, otherwise returns
    unmodified.

         >>> _optional_ns_fullname("tag")
         "tag"
         >>> _optional_ns_fullname("svg:width")
         "{http://www.w3.org/2000/svg}width"
    """
    i = name.find(":")
    if i >= 0:
        return ns_name(name[0:i], name[i+1:])
    else:
        return name

def _forced_ns_fullname(name, default = "xm"):
    """
    Ensures name contains full (long) namespace prefix. Handles
    properly non-prefixed names (to which default namespace is applied),
    shortcut-prefixed names (which are replaced with appropriate long names)
    and fully prefixed names (left as-is).
    """
    i = name.find(":")
    if i >= 0:
        return ns_name(name[0:i], name[i+1:])
    else:
        return ns_name(default, name)

def _forced_prefix(name, ns_shortcut = "xm"):
    """
    Adds short (colon) prefix if missing.
    """
    if not name.find(":") >= 0:
        name = "%s:%s" % (ns_shortcut, name)
    return name


class XmlHelper(object):
    """
    Map navigation helper. Written to provide identical API 
    for navigating just-created map and parsed map (which
    are represented a bit differently by lxml, thanks to
    namespace prefixes)
    """
    def __init__(self, is_creating, default = "xm"):
        self.is_creating = is_creating
        self.default = default

    def xpath_name(self, name):
        """
        Adapts name so it can be used in XPath expressions.
        """
        if self.is_creating:
            return name
        else:
            return "%s:%s" % (self.default, name)

    def create_child(self, parent, tag_name, **kwargs):
        """
        Create child of given XML element. tag_name can be simple
        ("subtag") or colon-prefixed ("svg:color").
        """
        if self.is_creating:
            return etree.SubElement(
                parent, _optional_ns_fullname(tag_name), **kwargs)
        else:
            return etree.SubElement(
                parent, _forced_ns_fullname(tag_name), **kwargs)

    ## TODO: ./ belo is probably not necessary

    def find_only_child(self, parent, tag_name, required = True):
        """
        Find child of given name, expecting it will be unique
        """
        if not self.is_creating:
            tag_name = "%s:%s" % (self.default, tag_name)
        return find_xpath(parent, "./" + tag_name, True, required)

    def find_children(self, parent, tag_name, require_non_empty = False):
        """
        Find all children of given name
        """
        if not self.is_creating:
            tag_name = "%s:%s" % (self.default, tag_name)
        return find_xpath(parent, "./" + tag_name, False, require_non_empty)

    def find_or_create_child(self, parent, tag_name):
        """
        If parent contains tag tag_name, returns its obj.
        Otherwise creates one and returns.
        """
        child = self.find_only_child(parent, tag_name, False)
        if child is None:
            child = self.create_child(parent, tag_name)  # ns
        return child
