# -*- coding: utf-8 -*-
"""
Base MimeType class
"""

class BaseMime(object):
	DEFAULT_TEXT = "text/plain"
	DEFAULT_BINARY = "application/octet-stream"
	ZERO_SIZE = "application/x-zerosize"

	def __init__(self, mime):
		self.__name = mime
		self._aliases = []
		self._comment = {}

	def __eq__(self, other):
		if isinstance(other, BaseMime):
			return self.name() == other.name()
		return self.name() == other

	def __repr__(self):
		return "<MimeType: %s>" % (self.name())

	def genericIcon(self):
		return self.genericMime().name().replace("/", "-")

	def genericMime(self):
		return self.__class__("%s/x-generic" % (self.type()))

	def icon(self):
		return self.name().replace("/", "-")

	def isDefault(self):
		name = self.name()
		return name == DEFAULT_BINARY or name == DEFAULT_TEXT

	def isInstance(self, other):
		return self == other or other in self.subClassOf()

	def name(self):
		return self.__name

	def subtype(self):
		return self.name().split("/")[1]

	def type(self):
		return self.name().split("/")[0]
