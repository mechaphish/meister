#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from farnsworth.models import PovTesterJob
from farnsworth.models import ValidPoll

import meister.creators
LOG = meister.creators.LOG.getChild('pov_tester')


class PovTesterCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        #
        # Step 1: For each CS
        # Step 2: Get current CS fielding for each team.
        # Step 3: Get current IDS fielding for each team.
        # Step 4: Check if there exists a result for corresponding CS_fielding hash and IDS_fielding hash
        # if yes, Skip
        # else, CREATE A POV TESTER JOB WITH HASHES, this is because, if we have already created
        # a job for that corresponding cs_fielding hash and ids_fielding hash
        # we do not re-create the job.
        # Get only polls for which scores have not been computed.
        for poll in ValidPoll.select().where(ValidPoll.has_scores_computed == False):
            target_cs = poll.cs
            # Create job for unpatched binary
            LOG.debug("Yielding CBTesterJob for poll %s (unpatched)", poll.id)
            yield CBTesterJob.get_or_create(payload={'poll_id': poll.id,
                                                     'cs_id': target_cs.id})

            # For each of patch types create Tester Jobs
            for patch_type in target_cs.cbns_by_patch_type():
                LOG.debug("Yielding CBTesterJob for poll %s (patched %s)", poll.id, patch_type)
                yield CBTesterJob.get_or_create(payload={'poll_id': poll.id,
                                                         'cs_id': target_cs.id,
                                                         'patch_type': patch_type})
            # Set scores computed flag and save
            poll.has_scores_computed = True
            poll.save()
