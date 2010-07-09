# -*- coding: utf-8 -*-
# (c) 2008-2010, Marcin Kasperski

"""
Embedded-id trick handling. See Topic.get_embedded_id for description
"""

PFX_EMBEDDED = "afaf"
PFX_OTHER = "bfbf"
PFX_LEN = 4

def qualify_id(id_text):
    """
    Check given id_text for embedded id. Returns it if present,
    otherwise return None.
    """
    if id_text.startswith(PFX_EMBEDDED):
        length = int(id_text[PFX_LEN:PFX_LEN+2])
        return id_text[-length:]
    else:
        return None

def unique_id(id_text):
    """
    Canonize topic identifier (internally either return embedded id
    if present in this identifier, or normal id with leading zeroes stripped).
    """
    embedded_id = qualify_id(id_text)
    if embedded_id:
        return embedded_id
    else:
        return id_text.lstrip("0")

class IdGen(object):
    """
    Generate unique identifiers for topics. Used internally.
    """
    def __init__(self,
                 length = 26):
        self.counter = 0
        self.length = length
        
    def next(self, embedded = None):
        """
        Give next unique id. If embedded is specified, embeds it inside.
        """
        self.counter += 1
        if embedded is None:
            suffix_len = self.length - PFX_LEN
            identifier = "%s%0*d" % (PFX_OTHER, suffix_len, self.counter)
            if len(identifier) > self.length:
                raise Exception("IdGen overflow")
            return identifier
        else:
            semb = str(embedded)
            lensemb = len(semb)
            
            # Structure:
            # - 4 chars - prefix
            # - 2 chars - length of embedded id
            # - 4 chars - counter (yeah, rotated if it overflows 10000)
            # - rest -  embedded id
            identifier = "%s%02d%04d" % (PFX_EMBEDDED, lensemb,
                                         self.counter % 10000)
            rest = self.length - PFX_LEN - 6
            if lensemb <= rest:
                identifier += "0" * (rest-lensemb)
            else:
                raise Exception(
                    "Embedded too long (%d, max %d)" % (lensemb, rest))
            identifier += semb
            if len(identifier) > self.length:
                raise Exception("EmbIdGen overflow")

            return identifier

if __name__ == "__main__":
    gen = IdGen()
    for x in range(1, 5):
        print gen.next()
        print gen.next(x * x * x)
        print gen.next("ABCDABCDABCDABCD")        
        print gen.next("ABCDABCDABCDABCD")
