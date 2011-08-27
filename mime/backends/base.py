"""
Base MimeType class
"""

class BaseMime(object):
	DEFAULT_TEXT = "text/plain"
	DEFAULT_BINARY = "application/octet-stream"

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

	def icon(self):
		return self.genericIcon() or self.name().replace("/", "-")

	def isDefault(self):
		name = self.name()
		return name == DEFAULT_BINARY or name == DEFAULT_TEXT

	def name(self):
		return self.__name

	def subtype(self):
		return self.name().split("/")[1]

	def type(self):
		return self.name().split("/")[0]
