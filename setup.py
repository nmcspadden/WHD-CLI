#!/usr/bin/env python

from setuptools import setup, find_packages

from whdcli import __version__

#http://stackoverflow.com/questions/10718767/have-the-same-readme-both-in-markdown-and-restructuredtext
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("Warning: pypandoc module not found, could not convert md to rst")
    read_md = lambda f: open(f, 'r').read()

setup(name = 'whd-cli',
      version = __version__,
      packages = find_packages(),
      package_data = {
          # Make sure to include Requests cacert.cer file
          '': ['*.pem', '*.md'],
      },
      description = 'Python wrapper for WHD REST API.',
      long_description = read_md('README.md'),
      author = 'Nick McSpadden',
      author_email = 'nmcspadden@gmail.com',
      url = 'https://github.com/nmcspadden/WHD-CLI',
      license = 'GPLv3',
      #install_requires=["requests"],
      classifiers = [
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)']
     )