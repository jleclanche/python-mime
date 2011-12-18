#!/usr/bin/env python
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
>>> MimeType.fromName("foo.TXT").name()
'text/plain'
>>> MimeType.fromName("foo.C").name()
'text/x-c++src'
>>> MimeType.fromName("foo.c").name()
'text/x-csrc'
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
>>> MimeType("application/zip").genericIcon()
'package-x-generic'
>>> MimeType("application/zip").icon()
'application-zip'
>>> MimeType("text/plain").genericIcon()
'text-x-generic'
>>> MimeType("application/zip").isInstance("application/zip")
True
>>> MimeType("application/x-chrome-extension").isInstance("application/zip")
True
>>> MimeType("text/plain").isInstance("application/zip")
False

Tests for MIME actions

>>> from mime.xdg.actions import ActionsFile
>>> f = open("mimeapps.list.tmp", "w")
>>> f.write('''
... [Added Associations]
... application/xml=kde4-kate.desktop;
... audio/x-mpegurl=smplayer2.desktop;kde4-kate.desktop;
... audio/x-scpls=smplayer2.desktop;;
... video/x-msvideo=smplayer2.desktop;;;mplayer.desktop;
... text/xml=google-chrome.desktop;
...
... [Default Applications]
... text/html=google-chrome.desktop
...
... [Removed Associations]
... application/xml=wine-extension-xml.desktop;kde4-kwrite.desktop;wine-extension-txt.desktop;
... '''
... )
>>> f.close()
>>> mimeapps = ActionsFile()
>>> mimeapps.parse(f.name)
>>> assocs = mimeapps.get("Added Associations")
>>> assocs["video/x-msvideo"]
['mplayer.desktop', 'smplayer2.desktop']
>>> assocs["audio/x-scpls"]
['smplayer2.desktop']
>>> assocs["audio/x-mpegurl"]
['kde4-kate.desktop', 'smplayer2.desktop']
>>> assocs["application/xml"]
['google-chrome.desktop', 'kde4-kate.desktop']
"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
