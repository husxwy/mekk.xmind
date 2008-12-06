# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.2.0'
long_description = open("README.txt").read()
classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.xmind',
      version=version,
      description="XMind data files reading and writing library.",
      long_description=long_description,
      classifiers=classifiers,
      keywords='xmind',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://mekk.waw.pl/python/xmind',
#      license='MIT',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe=False,
      install_requires=[
          'lxml',
      ],
#      entry_points="""
#      [babel.extractors]
#      mako = mako.ext.babelplugin:extract
#      """,
)
