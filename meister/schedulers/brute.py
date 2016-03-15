#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Brute scheduler.

Schedule everything whenver it is available.
"""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division


from requests.exceptions import RequestException

import meister.schedulers

LOG = meister.schedulers.LOG.getChild('brute')


class BruteScheduler(meister.schedulers.BaseScheduler):
    """Brute-force scheduler."""

    def __init__(self, **kwargs):
        """Create a brute-force scheduler object."""
        super(BruteScheduler, self).__init__(**kwargs)

    def run(self):
        """Run the brute scheduler."""
        LOG.debug("Starting brute scheduler")
        for job in self.jobs:
            LOG.debug("Scheduling %s for %s", job.__class__.__name__,
                      job.cbn_id)
            self.schedule(job)
