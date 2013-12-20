# -*- coding: utf-8 -*-

import unittest, sets

from mekk.xmind.id_gen import IdGen, qualify_id
import six

class EmbIdTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.id_gen = IdGen()

    def _testEmbedRecover(self, id):
        reply = self.id_gen.next(id)
        self.failUnlessEqual(id, qualify_id(reply))

    def testSimple(self):
        self._testEmbedRecover("1")
        self._testEmbedRecover("2")

    def testReal(self):
        self._testEmbedRecover("WiCkqHbUtLpLxZkF")
        self._testEmbedRecover("J9nZh0Q7JdMxHTOF")

    def testShort(self):
        self._testEmbedRecover("1")
        self._testEmbedRecover("3b")
        self._testEmbedRecover("3434234")

    def testZeroBased(self):
        self._testEmbedRecover("0Bzor4BbX9rtoQZO")
        self._testEmbedRecover("00B")
        
    def testNew(self):
        for i in range(0,10):
            r = six.advance_iterator(self.id_gen)
            self.failIf(qualify_id(r))

    def testDifferentNonPfx(self):
        s = sets.Set()
        for x in range(0, 10000):
            d = six.advance_iterator(self.id_gen)
            self.failIf(d in s)
            s.add(d)

    def testDifferentEmb(self):
        s = sets.Set()
        for emb in ["WiCkqHbUtLpLxZkF", "J9nZh0Q7JdMxHTOF", "Ala"]:
            for x in range(0, 2000):
                d = six.advance_iterator(self.id_gen)
                self.failIf(d in s)
                s.add(d)
