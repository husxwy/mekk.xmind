# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

"""
Zestaw stałych oraz funkcji użytkowych ułatwiających generowanie i przeszukiwanie
plików XML wykorzystywanych przez bibliotekę. Z szczególnym uwzględnieniem
namespaces.
"""

# Uwaga:
#
# Przy tworzeniu mapy posługujemy się nie-namespaceowanymi tagami i działa to dobrze.
# Przy analizie istniejącej, trzeba prefiksować namespace bo parser to gubi i znajduje
# tylko przy podaniu prefiksu. Bad luck

# TODO: rozważyć
#    //*[local-name()='bar']

from lxml import etree

class InternalStructureException(Exception):
    def __init__(self, text):
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

def ns_name(ns, what):
    """
    Generuje nazwę zawierającą namespace, np.

    >>> ns_name("svg", "x")
    "{http://www.w3.org/2000/svg}x"
    """
    return "{%s}%s" % (SEARCH_NSMAP[ns], what)

def find_xpath(parent, expression, single = False, required = False):
    """
    Wyszukuje w parent elementy spełniające wyrażenie xpath expression i zwraca
    wynik. Dołącza możliwość stosowania skrótów namespace (xm:topic, svg:color itd)

    Jeśli single jest ustawione, wymaga by znaleziono 0 lub 1 wyników i zwraca skalara
    (None lub wartość), gdy jest wiele wyników zgłasza wyjątek.
    Bez single zwraca listę.

    Jeśli required jest ustawione, rzuca wyjątek gdy nic nie znajdzie.
    """
    r = parent.xpath(expression, namespaces = SEARCH_NSMAP)
    if required and (not r):
        raise InternalStructureException(
            "Bad structure. Element %s not found under %s" % (expression, parent))
    if single:
        if len(r) > 1:
            raise InternalStructureException("Non-unique child %s under parent %s" % (tag_name, parent))
        elif r:
            r = r[0]
        else:
            r = None
    return r

############################################################################3
# Kontekstowe
############################################################################3

def _optional_ns_fullname(name):
    """
    Jeśli name zawiera dwukropek, robi na nim ns_name, wpp. nie robi nic.
    Np:
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
    i = name.find(":")
    if i >= 0:
        return ns_name(name[0:i], name[i+1:])
    else:
        return ns_name(default, name)

def _forced_prefix(name, ns = "xm"):
    """
    Jeśli nazwa nie zawiera dwukropka, dodaje go
    """
    if not name.find(":") >= 0:
        name = "%s:%s" % (ns, name)
    return name


class XmlHelper(object):
    """
    Klasa wspomagająca tworzenie i wyszukiwanie tagów. Główny cel: zapewnia
    identyczne API przy chodzeniu po stworzonej mapie i przy analizie sparsowanego
    XML (które lxml daje w różnych formach).
    """
    def __init__(self, is_creating, default = "xm"):
        self.is_creating = is_creating
        self.default = default

    def xpath_name(self, name):
        """
        Zwraca nazwę do użycia w wyrażeniach xpath
        """
        if self.is_creating:
            return name
        else:
            return "%s:%s" % (self.default, name)

    def create_child(self, parent, tag_name, **kwargs):
        """
        Tworzenie dziecka. Nazwa tagu to albo nazwa prosta ("subtag") albo prefiksowana ns
        ("svg:color").
        """
        if self.is_creating:
            return etree.SubElement(parent, _optional_ns_fullname(tag_name), **kwargs)
        else:
            return etree.SubElement(parent, _forced_ns_fullname(tag_name), **kwargs)

    ## TODO: ./ chyba można wywalić

    def find_only_child(self, parent, tag_name, required = True):
        if not self.is_creating:
            tag_name = "%s:%s" % (self.default, tag_name)
        return find_xpath(parent, "./" + tag_name, True, required)

    def find_children(self, parent, tag_name, require_non_empty = False):
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
