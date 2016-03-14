#!/usr/bin/python

"""
CGC - Team Interface Library

Copyright (C) 2015 - Brian Caswell <bmc@lungetech.com>
Copyright (C) 2015 - Tim <tim@0x90labs.com>

Adapted for MechanicalPhish by francesco@cs.ucsb.edu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


import binascii
import hashlib
import httplib
import os
import socket

import meister.cgc
from meister.cgc.tierror import TiError
from meister.cgc.endpoints.retrieval import TiRetrieval
from meister.cgc.endpoints.submission import TiSubmission

LOG = meister.cgc.LOG.getChild('ticlient')

class TiClient(TiSubmission, TiRetrieval):
    """
    Very basic example client demonstrating the CGC Team Interface
    """

    good_http = [200, 301]

    def __init__(self, ti_server, ti_port, user, password):
        self.ti_server = ti_server
        self.ti_port = ti_port
        self.user = user
        self.password = password
        self._LOG = LOG

    @classmethod
    def from_env(cls):
        """Create a TiClient Object from environment variables."""
        LOG.debug("Creating configuration from environment variables")
        host = os.environ['CGC_API_SERVICE_HOST']
        port = os.environ['CGC_API_SERVICE_PORT']
        user = os.environ['CGC_API_USER']
        password = os.environ['CGC_API_PASS']
        return cls(host, port, user, password)

    def user_id(self):
        return self.user.split('-')[1]

    def _make_request(self, uri, fields=None, files=None):
        """
        issues HTTP POST as multipart form data
        uri -- the uri location for POST
        fields -- sequence of (name,value) to encode into the form
        files -- sequence of (name,filename,filedata) into the form
        """

        headers = {'User-Agent': 'ti-client'}

        if fields is None:
            method = 'GET'
            content_type = None
            sendbody = None
        else:
            method = 'POST'
            content_type, sendbody = self._get_multipart_formdata(fields, files)

        try:
            conn = httplib.HTTPConnection(self.ti_server, self.ti_port)
            conn.request(method, uri, '', headers)
            rsp = conn.getresponse()
        except socket.error as err:
            raise TiError('unable to connect to server: %s:%s' % (self.ti_server, self.ti_port))
        except httplib.BadStatusLine as err:
            raise TiError('invalid request from server')

        body = rsp.read()

        if rsp.status != 401:
            LOG.debug("%s - %s - %s", rsp.status, rsp.reason, repr(body))
            raise TiError('server did not return digest auth information')

        parts = self._www_auth_parts(rsp.getheader('www-authenticate'))

        authorization = {}
        if 'algorithm' in parts:
            if parts['algorithm'].lower() != 'md5':
                raise TiError('unsupported digest algorithm')
            else:
                authorization['algorithm'] = parts['algorithm']

        for field in ['realm', 'nonce', 'qop']:
            authorization[field] = parts[field]

        # optional parts that should be copied
        for field in ['opaque']:
            if field in parts:
                authorization[field] = parts[field]

        authorization['username'] = self.user
        authorization['uri'] = uri
        authorization['nc'] = "00000001"
        authorization['cnonce'] = self._rand_str(4)

        authorization['response'] = self._gen_response(authorization, method)

        auth_string = "Digest " + ', '.join(['%s="%s"' % (k, v) for k, v in authorization.iteritems()])

        LOG.debug("# %s #", auth_string)

        if 'Content-Type' not in headers:
            headers['Content-Type'] = content_type

        headers['Authorization'] = auth_string

        try:
            conn.request(method, uri, sendbody, headers)
            rsp = conn.getresponse()
            data = rsp.read()
        except socket.error as err:
            raise TiError('unable to make request')
        except httplib.BadStatusLine:
            raise TiError('unknown error from server')

        LOG.debug("%s - %s", rsp.status, rsp.reason)

        conn.close()

        return rsp.status, rsp.reason, data

    def _get_multipart_formdata(self, fields, files):
        BOUNDARY = '------------------%s-cgc' % self._rand_str(8)
        builder = []
        for (name, value) in fields:
            builder.append('--' + BOUNDARY)
            builder.append('Content-Disposition: form-data; name="%s"' % name)
            builder.append('')
            builder.append(value)
        for (name, filename, value) in files:
            builder.append('--' + BOUNDARY)
            builder.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename))
            builder.append('Content-Type: application/octet-stream')
            builder.append('')
            builder.append(value)
        builder.append('--' + BOUNDARY + '--')
        builder.append('')
        body = '\r\n'.join(builder)

        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

        LOG.debug("type:%s, bodysize:%d", content_type, len(body))

        return content_type, body

    def _get_dl(self, dlpath, filename, expected_checksum):
        """
        issues HTTP GET to retreive an eval item for a team
        dlpath - the uri for the file to download (e.g. /dl/2/cb/...)
        """

        assert dlpath.startswith("/dl/"), "bad download path"

        status, reason, body = self._make_request(dlpath)

        checksum = hashlib.sha256(body).hexdigest()

        if expected_checksum != checksum:
            raise TiError('invalid download checksum.  Expected: %s Got: %s' % (expected_checksum, checksum))

        try:
            with open(filename, "wb") as w:
                w.write(body)
        except IOError as err:
            raise TiError('unable to write downloaded file')

    def _www_auth_parts(self, www_auth):
        """
        splits apart the www-authenticate parts for digest auth
        www_auth -- the www-authentication string to split
        """
        header = 'Digest '
        if not www_auth.startswith(header):
            raise TiError('invalid authentication response from server')

        www_auth = www_auth[len(header):]
        results = {}
        for item in www_auth.split(','):
            key, value = item.split('=')
            key = key.strip()
            value = value.strip('"')
            results[key] = value

        return results

    def _rand_str(self, string_len):
        """
        returns string of random bytes
        n -- number of bytes
        """
        return binascii.hexlify(os.urandom(string_len))

    def _gen_response(self, auth_d, method):
        """
        calculates HTTP digest auth respose
        auth_d -- dictionary of auth components required for response generation
        method -- the HTTP method (one of GET, POST)
        """
        ha1 = hashlib.md5("%s:%s:%s" % (auth_d['username'],
                                        auth_d['realm'],
                                        self.password)).hexdigest()

        ha2 = hashlib.md5("%s:%s" % (method, auth_d['uri'])).hexdigest()

        return hashlib.md5("%s:%s:%s:%s:%s:%s" % (ha1, auth_d['nonce'], auth_d['nc'],
                                                  auth_d['cnonce'],
                                                  auth_d['qop'],
                                                  ha2)).hexdigest()
