#!/usr/bin/env python
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

DEFAULT_MIME_TYPE = "application/octet-stream"

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


class MimeType(object):
	
	GLOBS = GlobsFile("/usr/share/mime/globs2")
	
	def __init__(self, mime):
		if mime not in self._mimes_map:
			mime = DEFAULT_MIME_TYPE
		self.__name = mime
	
	@classmethod
	def fromName(cls, name):
		mime = self.GLOBS.match(name)
		if mime:
			return cls(mime)
	
	def comment(self):
		pass
	
	def genericIcon(self):
		pass
	
	def icon(self):
		return self.genericIcon() or self.name().replace("/", "-")
	
	def name(self):
		return self.__name
	
	def parent(self):
		pass
