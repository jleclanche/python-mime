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
import struct
from fnmatch import fnmatch
from xml.dom import minidom, XML_NAMESPACE
from . import xdg
from ..basemime import BaseMime


class BaseFile(object):
	def __init__(self):
		self._keys = {}

	def __repr__(self):
		return self._keys.__repr__()

	def get(self, name, default=None):
		return self._keys.get(name, default)

class AliasesFile(BaseFile):
	"""
	/usr/share/mime/aliases
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, alias = line.split(" ")
				self._keys[mime] = alias

ALIASES = AliasesFile()
for f in xdg.getFiles("mime/aliases"):
	ALIASES.parse(f)


class GlobsFile(object):
	"""
	/usr/share/mime/globs2
	"""
	def __init__(self):
		self._extensions = {}
		self._literals = {}
		self._matches = []

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

				if "*" not in glob and "?" not in glob and "[" not in glob:
					self._literals[glob] = mime

				elif glob.startswith("*.") and "cs" not in flags:
					extension = glob[1:]
					if "*" not in extension and "?" not in extension and "[" not in extension:
						self._extensions[extension] = mime

				else:
					self._matches.append((int(weight), mime, glob, flags))

	def match(self, name):
		if name in self._literals:
			return self._literals[name]

		_, extension = os.path.splitext(name)
		if extension in self._extensions:
			return self._extensions[extension]
		elif extension.lower() in self._extensions:
			return self._extensions[extension.lower()]

		matches = []
		for weight, mime, glob, flags in self._matches:
			if fnmatch(name, glob):
				matches.append((weight, mime, glob))

			elif "cs" not in flags and fnmatch(name.lower(), glob):
				matches.append((weight, mime, glob))

		if not matches:
			return ""

		weight, mime, glob = max(matches, key=lambda weight_mime_glob: (weight_mime_glob[0], len(weight_mime_glob[2])))
		return mime

GLOBS = GlobsFile()
for f in xdg.getFiles("mime/globs2"):
	GLOBS.parse(f)


class IconsFile(BaseFile):
	"""
	/usr/share/mime/icons
	/usr/share/mime/generic-icons
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, icon = line.split(":")
				self._keys[mime] = icon

ICONS = IconsFile()
for f in xdg.getFiles("mime/generic-icons"):
	ICONS.parse(f)


class MagicFile(BaseFile):
	"""
	/usr/share/mime/magic
	"""
	class Magic(object):
		def __init__(self, *args):
			pass

	def readNumber(self, file):
		ret = bytearray()
		c = file.read(1)
		while c:
			if not c.isdigit():
				file.seek(-1, os.SEEK_CUR)
				break
			ret.append(ord(c))
			c = file.read(1)

		return ret and int(ret.decode("utf-8")) or 0

	def parse(self, path):
		with open(path, "rb") as file:
			if not file.read(12) == b"MIME-Magic\0\n":
				raise ValueError("Bad header for file %r" % (path))

			sections = []

			while True:
				# Parse the head
				# Expect a "["
				c = file.read(1)

				# Check if the file is empty
				if not c:
					return

				if c != b"[":
					raise ValueError("Section syntax error in %r: expected '[', got %r" % (file.name, c))
				priority, mime = self.parseSectionHead(file)
				if file.read(1) != b"\n":
					raise ValueError("Odd header in %r" % (file.name))

				# Parse the section(s)
				sections = []
				while True:
					c = file.read(1)
					if not c:
						return
					file.seek(-1, os.SEEK_CUR)
					if c != b"[":
						if c == b"\n": # end of file
							return
						else:
							sections.append(self.parseSectionBody(file))
					else:
						break

				# Store it all
				if mime not in self._keys:
					self._keys[mime] = []
				self._keys[mime].append((priority, sections))

	def parseSectionHead(self, file):
		"""
		Parse head of a section
		[50:text/x-diff]\n
		"""
		s = bytearray()
		while True:
			c = file.read(1)
			if not c:
				raise ValueError("Unfinished header in %r" % (file.name))
			if c == b"]":
				break
			s.append(ord(c))

		if b":" not in s:
			raise ValueError("No ':' in section header %r" % (s))

		s = s.decode("utf-8")
		priority, type = s.split(":")
		return priority, type

	def parseSectionBody(self, file):
		"""
		Parse line of a section
		[ indent ] ">" start-offset "=" value [ "&" mask ] [ "~" word-size ] [ "+" range-length ] "\n"
		"""
		indent = None
		c = file.read(1)
		if not c:
			raise ValueError("Early EOF")

		if c != b">":
			file.seek(-1, os.SEEK_CUR)
			indent = self.readNumber(file)
			c = file.read(1)
			if c != b">":
				raise ValueError("Missing '>' in section body (got %r)" % (c))

		startOffset = self.readNumber(file)

		c = file.read(1)

		if c != b"=":
			raise ValueError("Missing '=' in %r section body (got %r)" % (file.name, c))

		valueLength, = struct.unpack(">H", file.read(2))
		value = file.read(valueLength)

		invalidLine = False
		c = file.read(1)
		while True:
			if c == b"\n":
				# Done with the section
				break
			elif c == b"&":
				match = file.read(valueLength)
				break
			elif c == b"~":
				wordSize = self.readNumber(file)
				break
			elif c == b"+":
				rangeLength = self.readNumber(file)
				break
			elif not c:
				raise ValueError("Unexpected EOF in section body")
			else:
				raise ValueError("Unexpected character in section body: %r" % (c))

			# TODO unknown character, see kmimetyperepository.cpp

		return self.Magic(indent, startOffset, valueLength, value)


MAGIC = MagicFile()
for f in xdg.getFiles("mime/magic"):
	MAGIC.parse(f)


class SubclassesFile(BaseFile):
	"""
	/usr/share/mime/subclasses
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, subclass = line.split(" ")
				if mime not in self._keys:
					self._keys[mime] = []
				self._keys[mime].append(subclass)

SUBCLASSES = SubclassesFile()
for f in xdg.getFiles("mime/subclasses"):
	SUBCLASSES.parse(f)

class MimeType(BaseMime):
	"""
	XDG-based MimeType
	"""

	@staticmethod
	def installPackage(package, base=os.path.join(xdg.XDG_DATA_HOME, "mime")):
		from shutil import copyfile
		path = os.path.join(base, "packages")
		if not os.path.exists(path):
			os.makedirs(path)
		copyfile(package, os.path.join(path, os.path.basename(package)))
		xdg.updateMimeDatabase(base)

	@classmethod
	def fromName(cls, name):
		mime = GLOBS.match(name)
		if mime:
			return cls(mime)

	@classmethod
	def fromContent(cls, name):
		try:
			size = os.stat(name).st_size
		except IOError:
			return

		if size == 0:
			return cls(cls.ZERO_SIZE)

	def aliases(self):
		if not self._aliases:
			files = xdg.getFiles(os.path.join("mime", self.type(), "%s.xml" % (self.subtype())))
			if not files:
				return

			for file in files:
				doc = minidom.parse(file)
				for node in doc.documentElement.getElementsByTagName("alias"):
					alias = node.getAttribute("type")
					if alias not in self._aliases:
						self._aliases.append(alias)

		return self._aliases

	def aliasOf(self):
		return ALIASES.get(self.name())

	def comment(self, lang="en"):
		if lang not in self._comment:
			files = xdg.getFiles(os.path.join("mime", self.type(), "%s.xml" % (self.subtype())))
			if not files:
				return

			for file in files:
				doc = minidom.parse(file)
				for comment in doc.documentElement.getElementsByTagNameNS(xdg.FREEDESKTOP_NS, "comment"):
					nslang = comment.getAttributeNS(XML_NAMESPACE, "lang") or "en"
					if nslang == lang:
						self._comment[lang] = "".join(n.nodeValue for n in comment.childNodes).strip()
						break

		if lang in self._comment:
			return self._comment[lang]

	def genericIcon(self):
		return ICONS.get(self.name()) or super(MimeType, self).genericIcon()

	def subClassOf(self):
		return [MimeType(mime) for mime in SUBCLASSES.get(self.name(), [])]

	# MIME Actions

	def associations(self):
		from . import actions
		return actions.associationsFor(self.name())

	def bestApplication(self):
		from . import actions
		return actions.bestApplication(self.name())

	def defaultApplication(self):
		from . import actions
		return actions.defaultApplication(self.name())
