#!/usr/bin/env/python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import CBTesterJob, ValidPoll, CBPollPerformance, ChallengeSet

import meister.creators
LOG = meister.creators.LOG.getChild('cb_tester')


class CBTesterCreator(meister.creators.BaseCreator):
    MIN_TESTED_POLLS = 10000    # Number of polls we want to be tested for each CB

    @property
    def jobs(self):
        for cs in ChallengeSet.fielded_in_round():
            # For each of patch types create Tester Jobs
            for patch_type in cs.cbns_by_patch_type():
                # Get only polls for which scores have not been computed.
                for poll in CBPollPerformance.get_untested_polls(cs, patch_type):
                    curr_cb_tester_job = CBTesterJob(cs=poll.cs, payload={'poll_id': poll.id,
                                                                          'cs_id': poll.cs.id,
                                                                          'patch_type': patch_type},
                                                     limit_cpu=20, limit_memory=4096*2)

                    num_tested_polls = CBPollPerformance.num_tested_polls(poll.cs, patch_type)
                    priority = 100 if num_tested_polls < CBTesterCreator.MIN_TESTED_POLLS else 50

                    LOG.debug("Yielding CBTesterJob for poll %s (patched %s)", poll.id, patch_type)
                    yield (curr_cb_tester_job, priority)

            # Create jobs for unpatched binary for untested polls
            for poll in CBPollPerformance.get_untested_polls(cs, None):
                # Create job for unpatched binary
                curr_cb_tester_job = CBTesterJob(cs=poll.cs, payload={'poll_id': poll.id,
                                                                      'cs_id': poll.cs.id},
                                                 limit_cpu=20, limit_memory=4096*2)

                # get number of successful polls tested against unpatched binary
                num_tested_polls = CBPollPerformance.num_tested_polls(poll.cs, None)
                priority = 100 if num_tested_polls < CBTesterCreator.MIN_TESTED_POLLS else 50

                LOG.debug("Yielding CBTesterJob for poll %s (unpatched)", poll.id)
                yield (curr_cb_tester_job, priority)
