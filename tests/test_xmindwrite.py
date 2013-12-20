# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from __future__ import unicode_literals

import unittest
import zipfile
import tempfile
import os
import re
from lxml import objectify, etree
from sample_maps import generate_simple
import six

def linewiseEnsureEqual(testcase, expected, obtained,
                        ignoreInternalId = False,
                        ignoreTrailingEmptyLines = False,
                        showLongerPart = False):
    """
    Porównuje czy teksty expected i obtained są identyczne ale błędy raportuje liniowo,
    tj. podając w którym wierszu nastąpiła rozbieżność.
    W razie rozbieżności woła fail, inaczej nic nie robi.
    ignoreDateTimeMismatch powoduje ignorowanie wierszy PGN z datą/czasem
    """
    if not isinstance(obtained, six.string_types):
        raise AssertionError("Obtained data are not string: " + str(obtained))
    obtainedlines = obtained.split('\n')
    expectedlines = expected.split('\n')
    if ignoreTrailingEmptyLines:
        while obtainedlines and obtainedlines[-1] == "":
            obtainedlines.pop()
        while expectedlines and expectedlines[-1] == "":
            expectedlines.pop()
    obtainedsize = len(obtainedlines)
    expectedsize = len(expectedlines)

        #if not pats == gots:
        #    self.fail("File %s mismatch.\nOriginal:\n%s\nCreated:\n%s" % (name, pat, got))

    if ignoreInternalId:
        re_patch_id = re.compile('id="bfbf\d+"')

    for i in range(0, min(obtainedsize, expectedsize)):
        obt = obtainedlines[i]
        exp = expectedlines[i]
        if ignoreInternalId:
            obt = re_patch_id.sub('id="bfbf1234"', obt)
            exp = re_patch_id.sub('id="bfbf1234"', exp)
        if obt == exp:
            continue
        commonpfx = os.path.commonprefix([obt, exp])
        cpl = len(commonpfx)
        if showLongerPart:
            if i < obtainedsize - 1:
                obt = obt + "\n" + obtainedlines[i+1]
            if i < expectedsize - 1:
                exp = exp + "\n" + expectedlines[i+1]
            if i > 0:
                obt = obtainedlines[i-1] + "\n" + obt
                exp = expectedlines[i-1] + "\n" + exp
            testcase.fail(
                ("Line %d mismatch at pos %d.\n" % (i+1, cpl))
                + "\nObtained:\n"
                + obt
                + "\nExpected:\n"
                + exp)
        else:
            if cpl < 20:
                expdiag = exp[0:cpl+15]
                obtdiag = obt[0:cpl+15]
            else:
                expdiag = "..." + exp[cpl-10:cpl+15]
                obtdiag = "..." + obt[cpl-10:cpl+15]
            testcase.fail("Line %d mismatch at pos %d.\nExpected: '%s'\nobtained: '%s'" % (i+1, cpl, expdiag, obtdiag))
    if obtainedsize > expectedsize:
        if obtainedsize > expectedsize + 10:
            replines = obtainedlines[expectedsize:expectedsize+9] + ['...']
        else:
            replines = obtainedlines[expectedsize:]
        testcase.fail("Got %d extra line(s): %s" % (obtainedsize-expectedsize, "\n".join(replines)))
    elif expectedsize > obtainedsize:
        if obtainedsize < expectedsize - 10:
            replines = expectedlines[obtainedsize:obtainedsize+9] + ['...']
        else:
            replines = expectedlines[obtainedsize:]
        testcase.fail("Missing %d line(s): %s" % (expectedsize-obtainedsize, "\n".join(expectedlines[obtainedsize:])))

class MapCompareBase(object):
    """
    Bazowa klasa dla testów porównujących wygenerowaną mapę z wzorcem.
    Podklasa definiuje:
    - funkcję generate,
    - atrybut pattern_file
    """
    def generate(self):
        """
        Ma zwrócić obiekt document gotowy do zawołania .save
        """
        raise NotImplementedError
    def setUp(self):
        pf = self.pattern_file
        if not os.path.isfile(pf):
            pf = os.path.join("tests", pf)
        self.pattern = zipfile.ZipFile(pf, "r")
        fd, self.tfname = tempfile.mkstemp(".zip")
        self.generate().save(self.tfname)
        self.generated = zipfile.ZipFile(self.tfname, "r")
    def tearDown(self):
        self.generated.close()
        os.remove(self.tfname)
    def testSameMembers(self):
        self.assertEqual(
                         sorted(self.pattern.namelist()),
                         sorted(self.generated.namelist()),
                         )
    def testSameContent(self):
        return self._sameXml("content.xml")
    def testSameStyle(self):
        return self._sameXml("styles.xml")
    def testSameManifest(self):
        return self._sameXml("META-INF/manifest.xml")
    def testSameMeta(self):
        return self._sameXml("meta.xml")
    def _sameXml(self, name):
        #pat = self.pattern.read(name).decode("utf-8")
        #got = self.generated.read(name).decode("utf-8")
        # Normalize (to sort attributes). Note: this is not formally proven,
        # if fails, another method may be needed
        patobj = objectify.fromstring(self.pattern.read(name))
        gotobj = objectify.fromstring(self.generated.read(name))
        pat = etree.tostring(patobj, pretty_print=True)
        got = etree.tostring(gotobj, pretty_print=True)
        linewiseEnsureEqual(self, pat, got,
                            ignoreInternalId = True,
                            showLongerPart = True)

class SimpleMapTestCase(MapCompareBase, unittest.TestCase):
    pattern_file = "simple.xmind"
    def generate(self):
        return generate_simple()

