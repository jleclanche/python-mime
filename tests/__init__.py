# -*- coding: utf-8 -*-

from mime import MimeType

def main():
	mime = MimeType.fromName("foo.txt")
	assert mime.name() == "text/plain"
	assert mime.comment() == "plain text document"
	assert mime.comment(lang="fr") == "document texte brut"
	assert mime.type() == "text"
	assert mime.subtype() == "plain"

	mime = MimeType("text/x-lua")
	assert mime.comment() == "Lua script"

	mime = MimeType("application/x-does-not-exist")
	assert mime.comment() is None

	mime = MimeType.fromName("foo.mkv")
	assert mime.name() == "video/x-matroska"

	mime = MimeType("application/javascript")
	assert mime.aliases() == [u"application/x-javascript", u"text/javascript"]

	mime = MimeType("text/xml")
	assert mime.alias() == "application/xml"

	mime = MimeType("text/x-python")
	assert mime.subClassOf() == [u"application/x-executable", u"text/plain"]

if __name__ == "__main__":
	main()
