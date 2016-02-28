#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Run the meister."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import base64
from os import environ as ENV
from time import sleep

from requests.exceptions import RequestException

from farnsworth_client.api import API as ProfAPI
from farnsworth_client.models import ChallengeBinaryNode

import meister.cgc_client.api

from meister.schedulers.afl_scheduler import AFLScheduler


def main():
    cgc = meister.cgc_client.api.from_env()
    prof_url = "http://{}:{}".format(ENV['FARNSWORTH_SERVICE_HOST'],
                                     ENV['FARNSWORTH_SERVICE_PORT'])
    ProfAPI.init(prof_url)

    while True:
        try:
            round_n = cgc.status()['round']
            # FIXME: Use log
            print("[Meister] Round # {}".format(round_n))
            binaries = cgc.binaries(round_n)['binaries']
            for binary in binaries:
                cbn = ChallengeBinaryNode.find_by(name=binary['cbid'],
                                                  parent_id=None)
                if cbn is None:
                    blob = base64.b64decode(binary['data'])
                    cbn = ChallengeBinaryNode.create(name=binary['cbid'],
                                                     blob=blob,
                                                     parent_id=None)
                AFLScheduler().schedule(cbn=cbn, cpus=4, memory=1)

        except RequestException as ex:
            print("[Meister] ERROR: {}".format(type(ex)))

        sleep(3)

if __name__ == "__main__":
    main()
