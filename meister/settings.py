#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Load settings from environment variables."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

from os.path import join, dirname

# pylint: disable=import-error
from dotenv import load_dotenv
# pylint: enable=import-error

load_dotenv(join(dirname(__file__), '../.env'))
