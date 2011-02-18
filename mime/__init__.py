#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if os.name == "posix":
	from .backends.linux import MimeType
elif os.name == "nt":
	from .backends.windows import MimeType
else:
	raise NotImplementedError("MimeType not implemented for %r backend" % (os.name))
