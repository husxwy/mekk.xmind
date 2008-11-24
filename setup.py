# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.1.0'
setup(name='mekk.xmind',
      version=version,
      description="XMind data files reading and writing library.",
      long_description="""\
mekk.xmind makes it possible to generate XMind data files from python
script and also to read and analyze XMind files.

Mercurial repository:
<http://TODO:>

""",
      classifiers=[
#      'Development Status :: 4 - Beta',
#      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
#      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='xmind',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://mekk.waw.pl/python/xmind',
#      license='MIT',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
          'lxml',
      ],
#      entry_points="""
#      [babel.extractors]
#      mako = mako.ext.babelplugin:extract
#      """,
)
