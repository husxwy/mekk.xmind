# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

PFX_EMBEDDED = "afaf"
PFX_OTHER = "bfbf"
PFX_LEN = 4

EMBEDDED_LENGTH = 16

def qualify_id(id, embedded_length = EMBEDDED_LENGTH):
    """
    Jeśli w podanym identyfikatorze jest zakopany ukryty
    identyfikator, zwraca go. W przeciwnym wypadku
    zwraca None.
    """
    if id.startswith(PFX_EMBEDDED):
        ln = int(id[PFX_LEN:PFX_LEN+2])
        return id[-ln:]
    else:
        return None

def unique_id(id, embedded_length = EMBEDDED_LENGTH):
    n = qualify_id(id, embedded_length)
    if n:
        return n
    return id.lstrip("0")

class IdGen(object):
    """
    Generator identyfikatorów uwzględniający możliwość
    wklejania w id zewnętrznego identyfikatora.
    """
    def __init__(self,
                 length = 26,
                 embedded_length = EMBEDDED_LENGTH):
        self.counter = 0
        self.length = length
        self.embedded_length = embedded_length
        
    def next(self, embedded = None):
        self.counter += 1
        if embedded is None:
            suffix_len = self.length - PFX_LEN
            no = "%s%0*d" % (PFX_OTHER, suffix_len, self.counter)
            if len(no) > self.length:
                raise Exception("IdGen overflow")
            return no
        else:
            semb = str(embedded)
            lensemb = len(semb)
            
            # 4 znaki prefiksu
            # 2 znaki długości zanurzonego (maks 16)
            # <=4  countera (ale olewam i rotuję)
            # <=16 zanurzonego
            r = "%s%02d%04d" % (PFX_EMBEDDED, lensemb,
                                self.counter % 10000)
            rest = self.length - PFX_LEN - 6
            if lensemb <= rest:
                r += "0" * (rest-lensemb)
            else:
                raise Exception("Embedded too long (max %d)" % self.embedded_legth)
            r += semb
            if len(r) > self.length:
                raise Exception("EmbIdGen overflow")

            return r

if __name__ == "__main__":
    e = IdGen()
    for x in range(1,5):
        print e.next()
        print e.next(x * x * x)
        print e.next("ABCDABCDABCDABCD")        
        print e.next("ABCDABCDABCDABCD")
