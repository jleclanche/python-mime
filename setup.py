#!/usr/bin/env python

import os.path
from distutils.core import setup

#README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

CLASSIFIERS = [
	"Development Status :: 5 - Production/Stable",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: MIT License",
	"Programming Language :: Python",
]

setup(
	name = "python-mime",
	packages = ["mime", "mime.windows", "mime.xdg"],
	py_modules = ["mime.basemime"],
	author = "Jerome Leclanche",
	author_email = "adys.wh@gmail.com",
	classifiers = CLASSIFIERS,
	description = "Implementation of the XDG Shared MIME Info spec version 0.20.",
	download_url = "http://github.com/Adys/python-mime/tarball/master",
	#long_description = README,
	url = "http://github.com/Adys/python-mime",
	version = "1.0",
)
