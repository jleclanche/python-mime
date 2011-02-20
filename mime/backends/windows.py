# -*- coding: utf-8 -*-

from os.path import splitext
from _winreg import HKEY_CLASSES_ROOT, OpenKey, QueryValueEx
from .base import BaseMime

class MimeType(BaseMime):
	def __init__(self, mime):
		self.__name = mime
		self.__comment = None
	
	@classmethod
	def fromName(cls, name):
		root, ext = splitext(name.lower())
		if ext is ".":
			ext = root
		ext = ext or root
		
		try:
			with OpenKey(HKEY_CLASSES_ROOT, ext) as key:
				try:
					mime, _ = QueryValueEx(key, "Content Type")
					instance = cls(mime)
				except WindowsError:
					instance = cls("application/x-windows-extension-%s" % (ext[1:]))
				instance.__handlekey, _ = QueryValueEx(key, "") # (Default)
				return instance
		except WindowsError:
			pass
	
	def comment(self, lang="en"):
		if self.__comment is None:
			with OpenKey(HKEY_CLASSES_ROOT, self.__handlekey) as key:
				self.__comment, _ = QueryValueEx(key, "") # (Default)
		
		return self.__comment
	
	def genericIcon(self):
		pass
	
	def icon(self):
		return self.genericIcon() or self.name().replace("/", "-")
	
	def isDefault(self):
		name = self.name()
		return name == DEFAULT_BINARY or name == DEFAULT_TEXT
	
	def name(self):
		return self.__name
	
	def parent(self):
		pass
