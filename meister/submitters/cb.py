#!/usr/bin/env python

import random
from farnsworth.models import ChallengeBinaryNode, IDSRule
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc
        self.patch_submission_order = None
        self.submission_index = 0
        self.available_patch_types = set()

    def run(self, current_round, random_submit=False):
        pass
        # submit only in odd rounds, see FAQ163 & FAQ157
        # if (current_round % 2) == 1:
        #     to_submit_patch_type = None
        #     to_submit_patch_types = None
        #     if self.patch_submission_order is not None:
        #         if self.submission_index >= (len(self.patch_submission_order) - 2):
        #                 self.submission_index = 0
        #         to_submit_patch_types = self.patch_submission_order[self.submission_index:]
        #         self.submission_index += 1
        #     submit_pt_index = 0
        #     for cbn in ChallengeBinaryNode.roots():
        #         # submitted_ids = cbn.cs.ids_rules.where(IDSRule.submitted_at.is_null(True))
        #         # # dont' submit CB that has IDS active
        #         # if len(submitted_ids) > 0:
        #         #     continue
        #         # # submit patches for 50% of binaries, so we can test IDs on the other 50%
        #         # if random_submit and (random.randint(0,1) == 0):
        #         #     continue
        #         curr_patch_types = set(cbn.cs.cbns_by_patch_type().keys())
        #         if self.patch_submission_order is None or to_submit_patch_types is None or \
        #                 len(curr_patch_types.symmetric_difference(self.available_patch_types)):
        #             self.available_patch_types = curr_patch_types
        #             all_patch_types = map(lambda x: str(x), list(cbn.cs.cbns_by_patch_type().keys()))
        #             self.patch_submission_order = all_patch_types * 1000
        #             self.submission_index = 0
        #             to_submit_patch_types = self.patch_submission_order[self.submission_index:]
        #             self.submission_index += 1

        #         if submit_pt_index >= len(to_submit_patch_types):
        #             submit_pt_index = 0

        #         if submit_pt_index < len(to_submit_patch_types):
        #             to_submit_patch_type = to_submit_patch_types[submit_pt_index]

        #         submit_pt_index += 1

        #         for patch in cs.unsubmitted_patches:
        #             if patch.patch_type is not None and (to_submit_patch_type is None or
        #                                                  to_submit_patch_type == str(patch.patch_type)):
        #                 LOG.info("Submitting patch %s for %s on round %s",
        #                                  patch.name, cbn.name, current_round)
        #                 try:
        #                     self._cgc.uploadRCB(str(cbn.cs.name), (str(cbn.name), str(patch.blob)))
        #                     cs.submit_patches(patch)
        #                     # FIXME: we submit only one patch type at once
        #                     break
        #                 except TiError as e:
        #                     LOG.error("Submission error: %s", e.message)
        #             else:
        #                 LOG.info("Ignoring patch %s for %s as to submit patch type is %s", str(patch.name),
        #                          str(cbn.name), str(to_submit_patch_type))
