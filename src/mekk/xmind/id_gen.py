# -*- coding: utf-8 -*-

PFX_EMBEDDED = "afaf"
PFX_OTHER = "bfbf"
EMBEDDED_LENGTH = 16

def simple_id_gen(prefix, length = 26):
    """
    Prosty generator identyfikatorów z zadanym prefiksem i o zadanej długości.
    """
    suffix_len = length - len(prefix)
    count = 0
    while True:
        count += 1
        no = "%s%0*d" % (prefix, suffix_len, count)
        if len(no) > length:
            break
        yield no

def qualify_id(id, embedded_length = EMBEDDED_LENGTH):
    """
    Jeśli w podanym identyfikatorze jest zakopany ukryty
    identyfikator, zwraca go. W przeciwnym wypadku
    zwraca None.
    """
    if id.startswith(PFX_EMBEDDED):
        return id[-embedded_length:].lstrip("0")
    else:
        return None

def unique_id(id, embedded_length = EMBEDDED_LENGTH):
    if id.startswith(PFX_EMBEDDED) or id.startswith(PFX_OTHER):
        return id[-embedded_length:].lstrip("0")
    else:
        return id.lstrip("0")

class IdGen(object):
    """
    Generator identyfikatorów uwzględniający możliwość
    wklejania w id zewnętrznego identyfikatora.
    """
    def __init__(self,
                 length = 26,
                 embedded_length = EMBEDDED_LENGTH):
        self.simplegen = simple_id_gen(PFX_OTHER, length)
        self.embgen = simple_id_gen(PFX_EMBEDDED, length - embedded_length)
        self.embedded_length = embedded_length
    def __del__(self):
        self.simplegen.close()
        self.embgen.close()
    def next(self, embedded = None):
        if embedded is None:
            return self.simplegen.next()
        else:
            semb = str(embedded)
            return self.embgen.next() + ("0" * (self.embedded_length - len(semb))) + semb

if __name__ == "__main__":
    t = simple_id_gen(length = 16, prefix = "ABCD")
    for x in range(0,15):
        print t.next()
    t.close()
    e = IdGen()
    for x in range(1,5):
        print e.next()
        print e.next(x * x * x)
