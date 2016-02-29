#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Meister log settings."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import logging
import os
import sys

DEFAULT_FORMAT = '%(asctime)s - %(name)-30s - %(levelname)-10s - %(message)s'

LOG = logging.getLogger('meister')
LOG.setLevel(os.environ.get('MEISTER_LOG_LEVEL', logging.WARNING))

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(os.environ.get('MEISTER_LOG_FORMAT',
                                                      DEFAULT_FORMAT)))
LOG.addHandler(handler)
