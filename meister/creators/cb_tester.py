#!/usr/bin/env/python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import CBTesterJob, ValidPoll, CBPollPerformance

import meister.creators
LOG = meister.creators.LOG.getChild('cb_tester')


class CBTesterCreator(meister.creators.BaseCreator):
    MIN_PASSED_POLLS = 10000    # Number of polls we want to be tested for each CB

    @property
    def jobs(self):
        # Get only polls for which scores have not been computed.
        # FIXME: query is incorrect for creator technique
        for poll in ValidPoll.select().where(ValidPoll.has_scores_computed == False):
            # Create job for unpatched binary
            LOG.debug("Yielding CBTesterJob for poll %s (unpatched)", poll.id)
            curr_cb_tester_job = CBTesterJob(cs=poll.cs, payload={'poll_id': poll.id,
                                                                  'cs_id': poll.cs.id},
                                             limit_cpu=20, limit_memory=4096)

            # get number of successful polls tested against unpatched binary
            num_success_polls = CBPollPerformance.num_success_polls(poll.cs, None)
            priority = 100 if num_success_polls < CBTesterCreator.MIN_PASSED_POLLS else 50

            LOG.debug("Yielding CBTesterJob for poll %s (unpatched)", poll.id)
            yield (curr_cb_tester_job, priority)

            # For each of patch types create Tester Jobs
            for patch_type in poll.cs.cbns_by_patch_type():
                num_success_polls = CBPollPerformance.num_success_polls(poll.cs, patch_type)
                priority = 100 if num_success_polls < CBTesterCreator.MIN_PASSED_POLLS else 50
                curr_cb_tester_job = CBTesterJob(cs=poll.cs, payload={'poll_id': poll.id,
                                                                        'cs_id': poll.cs.id,
                                                                        'patch_type': patch_type},
                                                 limit_cpu=20, limit_memory=4096)

                LOG.debug("Yielding CBTesterJob for poll %s (patched %s)", poll.id, patch_type)
                yield (curr_cb_tester_job, priority)
