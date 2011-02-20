# -*- coding: utf-8 -*-
"""
Implementation of the XDG Shared MIME Info spec version 0.20.
http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-0.20.html

Loosely based on python-xdg and following the Qt code style.

Applications can install information about MIME types by storing an
XML file as <MIME>/packages/<application>.xml and running the
update-mime-database command, which is provided by the freedesktop.org
shared mime database package.
"""

import os
from fnmatch import fnmatch
from xml.dom import minidom, XML_NAMESPACE
from .base import BaseMime

FREEDESKTOP_NS = "http://www.freedesktop.org/standards/shared-mime-info"

HOME = os.path.expanduser("~")
XDG_DATA_HOME   = os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))
XDG_DATA_DIRS   = set([XDG_DATA_HOME] + os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"))
# XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
# XDG_CONFIG_DIRS = set([XDG_CONFIG_HOME] + os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":"))
# XDG_CACHE_HOME  = os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache"))

def getFiles(name):
	ret = []
	for dir in XDG_DATA_DIRS:
		path = os.path.join(dir, "mime", name)
		if os.path.exists(path):
			ret.append(path)
	return ret

class GlobsFile(object):
	"""
	/usr/share/mime/globs2
	"""
	def __init__(self):
		self.__matches = []
		self.__literals = {}
	
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.startswith("#"): # comment
					continue
				
				if line.endswith("\n"):
					line = line[:-1]
				
				weight, _, line = line.partition(":")
				mime, _, line = line.partition(":")
				glob, _, line = line.partition(":")
				flags, _, line = line.partition(":")
				flags = flags and flags.split(",") or []
				
				self.__matches.append((int(weight), mime, glob, flags))
				
				if "*" not in glob and "?" not in glob and "[" not in glob:
					self.__literals[glob] = len(self.__matches)
	
	def match(self, name):
		if name in self.__literals:
			return self.__matches[self.__literals[name]][1]
		
		matches = []
		for weight, mime, glob, flags in self.__matches:
			if fnmatch(name, glob):
				matches.append((weight, mime, glob))
			
			elif "cs" not in flags and fnmatch(name.lower(), glob):
				matches.append((weight, mime, glob))
		
		if not matches:
			return ""
		
		weight, mime, glob = max(matches, key=lambda (weight, mime, glob): (weight, len(glob)))
		return mime

GLOBS = GlobsFile()
for f in getFiles("globs2"):
	GLOBS.parse(f)


class IconsFile(object):
	"""
	/usr/share/mime/icons
	/usr/share/mime/generic-icons
	"""
	def __init__(self):
		self.__icons = {}
	
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]
				
				mime, icon = line.split(":")
				self.__icons[mime] = icon
	
	def get(self, name):
		return self.__icons.get(name)

ICONS = IconsFile()
for f in getFiles("generic-icons"):
	ICONS.parse(f)


class MimeType(BaseMime):
	
	@classmethod
	def fromName(cls, name):
		mime = GLOBS.match(name)
		if mime:
			return cls(mime)
	
	def comment(self, lang="en"):
		if self._comment is None:
			doc = minidom.parse(self.BASE + self.name() + ".xml")
			for comment in doc.documentElement.getElementsByTagNameNS(FREEDESKTOP_NS, "comment"):
				nslang = comment.getAttributeNS(XML_NAMESPACE, "lang") or "en"
				if nslang == lang:
					self._comment = "".join(n.nodeValue for n in comment.childNodes).strip()
		
		return self._comment
	
	def genericIcon(self):
		return ICONS.get(self.name())
	
	def parent(self):
		pass
