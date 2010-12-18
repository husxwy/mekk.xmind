# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from setuptools import setup, find_packages

version = '0.5.0'
long_description = open("README.txt").read()

classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)",
    "License :: OSI Approved :: Artistic License",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    ]

license = "Artistic" # or MPL 1.1

setup(name='mekk.xmind',
      version=version,
      description="XMind data files reading and writing library.",
      long_description=long_description,
      classifiers=classifiers,
      keywords='xmind',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://bitbucket.org/Mekk/mekk.xmind/',
      license=license,
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe=False,
      install_requires=[
          'lxml >= 2.1.1',
      ],
)
