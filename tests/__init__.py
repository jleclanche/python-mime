# -*- coding: utf-8 -*-
"""
Tests for python-mime

>>> from mime import MimeType
>>> mime = MimeType.fromName("foo.txt")
>>> mime.name()
'text/plain'
>>> mime.comment()
u'plain text document'
>>> mime.comment(lang="fr")
u'document texte brut'
>>> mime.type()
'text'
>>> mime.subtype()
'plain'
>>> mime.genericMime()
<MimeType: text/x-generic>
>>> mime.genericMime().name()
'text/x-generic'
>>> MimeType("text/x-lua").comment()
u'Lua script'
>>> MimeType("application/x-does-not-exist")
<MimeType: application/x-does-not-exist>
>>> MimeType("application/x-does-not-exist").comment()
>>> MimeType.fromName("foo.mkv").name()
'video/x-matroska'
>>> MimeType("application/javascript").aliases()
[u'application/x-javascript', u'text/javascript']
>>> MimeType("text/xml").aliasOf()
'application/xml'
>>> MimeType("text/x-python").subClassOf()
[<MimeType: application/x-executable>, <MimeType: text/plain>]
"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
