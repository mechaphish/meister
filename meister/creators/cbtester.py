# -*- coding: utf-8 -*-

import meister.creators
from farnsworth.models import CBTesterJob
from farnsworth.models import ValidPoll

LOG = meister.creators.LOG.getChild('cb_tester')


class CbTesterCreator(meister.creators.BaseCreator):
    @property
    def jobs(self):
        # get only polls for which scores have not been computed.
        for curr_valid_poll in ValidPoll.select().where(ValidPoll.has_scores_computed == False and
                                                        ValidPoll.round == None):
            target_cs = curr_valid_poll.cs
            # create job for unpatched binary
            LOG.debug("Yielding CBTesterJob for Poll ID :%s for unpatched binary", curr_valid_poll.id)
            yield CBTesterJob.get_or_create(limit_cpu=-1, limit_memory=-1, payload={'poll_id': curr_valid_poll.id,
                                                                                    'cs_id': target_cs.id})
            all_patch_types = target_cs.cbns_by_patch_type()
            # for each of patch types create Tester Jobs
            for curr_patch_type in all_patch_types:
                LOG.debug("Yielding CBTesterJob for Poll ID :%s for patched binary %s", curr_valid_poll.id,
                          curr_patch_type)
                yield CBTesterJob.get_or_create(limit_cpu=-1, limit_memory=-1, payload={'poll_id': curr_valid_poll.id,
                                                                                        'cs_id': target_cs.id,
                                                                                        'patch_type': curr_patch_type})
