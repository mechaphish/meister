#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Load settings from environment variables."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

from os.path import join, dirname

from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '../.env'))
