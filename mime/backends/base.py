"""
Base MimeType class
"""

class BaseMime(object):
	DEFAULT_TEXT = "text/plain"
	DEFAULT_BINARY = "application/octet-stream"
	
	def __eq__(self, other):
		if isinstance(other, BaseMimeType):
			return self.name() == other.name()
		return self.name() == other
	
	def icon(self):
		return self.genericIcon() or self.name().replace("/", "-")
	
	def isDefault(self):
		name = self.name()
		return name == DEFAULT_BINARY or name == DEFAULT_TEXT
