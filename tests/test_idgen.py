# -*- coding: utf-8 -*-

import unittest

from mekk.xmind.id_gen import IdGen, qualify_id

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

    def testZeroBased(self):
        self._testEmbedRecover("0Bzor4BbX9rtoQZO")
        
    def testNew(self):
        for i in range(0,10):
            r = self.id_gen.next()
            self.failIf(qualify_id(r))
