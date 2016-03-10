#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Errors and Exceptions for the CGC API."""

class CGCAPIError(Exception):   # pylint: disable=missing-docstring
    """The default error for any CGC API errors."""
    def __init__(self, code, method, path, body=""):
        self.code = code
        self.method = method
        self.path = path
        self.body = body

    def __str__(self):
        return 'Error {} on {} {}: "{}"'.format(
            self.code, self.method, self.path, self.body)
