# -*- coding: utf-8 -*-

"""
Zestaw stałych oraz funkcji użytkowych ułatwiających generowanie i przeszukiwanie
plików XML wykorzystywanych przez bibliotekę. Z szczególnym uwzględnieniem
namespaces.
"""

# TODO: dać sobie spokój z tym śmietnikiem. Przejść z find-ów na xpath. A tam:
#     "./childname"
# i
#    //*[local-name()='bar']
# albo
#tree.getroot().xpath(
#     "//xhtml:img",
#     namespaces={'xhtml':'http://www.w3.org/1999/xhtml'}
#     )
#
# Uwaga: xpath zawsze zwraca listę

from lxml import etree

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

def ns_name(ns, what):
    """
    Generuje nazwę zawierającą namespace, np.

    >>> content_name("svg", "x")
    "{http://www.w3.org/2000/svg}x"
    """
    return "{%s}%s" % (SEARCH_NSMAP[ns], what)

def _find_child_tag(parent, tag_name, ns, allow_many = False):
    """
    Wyszukanie dziecka bez prefiksu namespaca a także z nim - tak, jak się uda.
    To pierwsze potrzebne przy budowaniu, to drugie przy parsowaniu.
    """
    child = parent.find(ns_name(ns, tag_name))
    #child = parent.find(tag_name)
    #if not child:
    #    child = parent.find("{%s}%s" % (SEARCH_NSMAP[ns], tag_name))
    if isinstance(child, list):
        if len(list) == 1:
            child = child[0]
        elif len(list) == 0:
            child = None
        elif not allow_many:
            raise Exception("Non-unique child %s under parent %s" % (tag_name, parent))
    return child

def find_or_create_tag(parent, tag_name, ns = "xm"):
    """
    If parent contains tag tag_name, returns its obj.
    Otherwise creates one and returns.
    """
    child = _find_child_tag(parent, tag_name, ns)
    if child is None:
        child = etree.SubElement(parent, tag_name)
    return child

def find_tag(parent, tag_name, ns = "xm"):
    child = _find_child_tag(parent, tag_name, ns)
    if child is None:
        #print etree.tostringlist(parent, pretty_print = True)
        raise Exception("Tag %(tag_name)s not found under %(parent)s\n" % locals()
                        + "Known children: " + ", ".join([t.tag for t in list(parent)]))
    return child

def find_tags(parent, tag_name, ns = "xm"):
    return _find_child_tag(parent, tag_name, ns, True)

