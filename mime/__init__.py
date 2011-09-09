#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if sys.platform == "win32":
	from .backends.windows import MimeType
else:
	from .backends.xdg import MimeType
