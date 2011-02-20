# -*- coding: utf-8 -*-

from os.path import splitext
from _winreg import HKEY_CLASSES_ROOT, OpenKey, QueryValueEx
from .base import BaseMime

class MimeType(BaseMime):
	"""
	Windows implementation for MimeType
	Uses the Windows Registry to query mimes
	"""
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
		if self._comment is None:
			with OpenKey(HKEY_CLASSES_ROOT, self.__handlekey) as key:
				self._comment, _ = QueryValueEx(key, "") # (Default)
		
		return self._comment
	
	def genericIcon(self):
		pass
	
	def parent(self):
		pass
