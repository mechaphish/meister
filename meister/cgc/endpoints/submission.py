import os
import json
import hashlib

from meister.cgc.tierror import TiError

class TiSubmission(object):
    def uploadRCB(self, csid, *binaries):
        """
        issues HTTP POST of a CS (single or multi-CB)
        csid -- CSID for the CS
        binaries -- list of (CBID,data) where data are the binary bytes
        """

        uri = "/rcb"

        fields = [("csid", csid)]
        uploads = []

        expected = {}

        for cbid, data in binaries:
            uploads.append((cbid, cbid, data))
            expected[cbid] = hashlib.sha256(data).hexdigest()

        status, reason, body = self._make_request('/rcb', fields, uploads)

        try:
            response = json.loads(body)
        except ValueError:
            raise TiError('unable to parse response from server')

        if status != 200:
            raise TiError(', '.join(response['error']))

        if len(expected.keys()) != len(response['files']):
            raise TiError('uploaded %d files, only %d processed' % (len(expected.keys()), len(response['files'])))

        for entry in response['files']:
            if entry['file'] not in expected:
                raise TiError('invalid file upload: %s' % entry['file'])

            if entry['hash'] != expected[entry['file']]:
                raise TiError('upload corrupted.  Expected: %s Got: %s' % (expected[entry['file']], entry['hash']))

        return response

    def uploadIDS(self, csid, data):
        fields = [("csid", csid)]
        uploads = []

        uploads.append(('file', 'ids_filename', data))

        status, reason, body = self._make_request('/ids', fields, uploads)

        expected = hashlib.sha256(data).hexdigest()

        try:
            response = json.loads(body)
        except ValueError:
            raise TiError('unable to parse response from server')

        if status == 200:
            if expected != response['hash']:
                raise TiError('uploaded hash does not match.  '
                              'Expected: %s Got: %s' % (expected,
                              response['hash']))
        else:
            raise TiError(', '.join(response['error']))

        return response

    def uploadPOV(self, csid, team, throws, data):
        fields = [("csid", csid), ('team', team), ('throws', throws)]
        uploads = []

        uploads.append(('file', 'pov_filename', data))

        status, reason, body = self._make_request('/pov', fields, uploads)

        expected = hashlib.sha256(data).hexdigest()

        try:
            response = json.loads(body)
        except ValueError:
            raise TiError('unable to parse response from server')

        if status == 200:
            if expected != response['hash']:
                raise TiError('uploaded hash does not match.  '
                              'Expected: %s Got: %s' % (expected,
                              response['hash']))
        else:
            raise TiError(', '.join(response['error']))

        return response
