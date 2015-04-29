# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

setup(
    name="django-import-redirects",
    version=__import__('import_redirects').__version__,
    license="GPLv3",
    keywords="django import redirects",

    author="Egor Slesarev",
    author_email="egor.slesarev@redsolution.ru",

    maintainer='Egor Slesarev',
    maintainer_email='egor.slesarev@redsolution.ru',

    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
