# -*- coding: utf-8 -*-
"""
Implementation of the XDG Shared MIME Info spec version 0.20.
http://www.freedesktop.org/standards/shared-mime-info-spec/

Loosely based on python-xdg and following the Qt code style.

Applications can install information about MIME types by storing an
XML file as <MIME>/packages/<application>.xml and running the
update-mime-database command, which is provided by the freedesktop.org
shared mime database package.
"""

import os.path
from fnmatch import fnmatch
from xml.dom import minidom, XML_NAMESPACE
from .base import BaseMime

FREEDESKTOP_NS = "http://www.freedesktop.org/standards/shared-mime-info"

class GlobsFile(object):
	"""
	/usr/share/mime/globs2
	"""
	def __init__(self, path):
		self.__file = open(path, "r")
		
		self.__matches = []
		self.__literals = {}
		
		self.__parse()
		self.__file.close()
	
	def __parse(self):
		for line in self.__file:
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

class IconsFile(object):
	"""
	/usr/share/mime/icons
	/usr/share/mime/generic-icons
	"""
	def __init__(self, path):
		self.__file = open(path, "r")
		
		self.__icons = {}
		
		self.__parse()
		self.__file.close()
	
	def __parse(self):
		for line in self.__file:
			if line.endswith("\n"):
				line = line[:-1]
			
			mime, icon = line.split(":")
			self.__icons[mime] = icon
	
	def get(self, name):
		return self.__icons.get(name)

class MimeType(BaseMime):
	
	BASE = "/usr/share/mime/"
	GLOBS = GlobsFile(BASE + "globs2")
	ICONS = IconsFile(BASE + "generic-icons")
	
	@classmethod
	def fromName(cls, name):
		mime = cls.GLOBS.match(name)
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
		return self.ICONS.get(self.name())
	
	def parent(self):
		pass
