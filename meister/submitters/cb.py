#!/usr/bin/env python

import random
from farnsworth.models import (ChallengeBinaryNode,
                               ChallengeSet,
                               CSSubmissionCable,
                               IDSRule)
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self):
        self.patch_submission_order = None
        self.submission_index = 0
        self.available_patch_types = set()

    def run(self, current_round=None, random_submit=False):
        small_list = None
        if self.patch_submission_order is not None:
            if self.submission_index >= len(self.patch_submission_order):
                self.submission_index = 0
            small_list = self.patch_submission_order[self.submission_index:]
        small_index = 0
        for cs in ChallengeSet.fielded_in_round():
            curr_patch_types = set(cs.cbns_by_patch_type().keys())
            to_submit_patch_type = None
            if self.patch_submission_order is None or \
                    not (curr_patch_types <= self.available_patch_types):
                self.available_patch_types = curr_patch_types
                all_patch_types = map(lambda x: str(x), list(cs.cbns_by_patch_type().keys()))
                self.patch_submission_order = all_patch_types * 1000
                self.submission_index = 0
                small_list = self.patch_submission_order[self.submission_index:]


            if small_index >= len(small_list):
                small_index = 0
            if small_index < len(small_list):
                to_submit_patch_type = small_list[small_index]
            small_index += 1
            print cs.name, to_submit_patch_type

            patches_to_submit = []
            for cbn in cs.cbns_original:
                for patch in cbn.unsubmitted_patches:
                    original_cbid = cbn.name
                    if patch.patch_type is not None and (to_submit_patch_type is None or
                                                         to_submit_patch_type == str(patch.patch_type)):
                        LOG.debug("Submitting patch %s for %s", patch.name, original_cbid)
                        patches_to_submit.append(patch)
                        # we submit only one patch type at once
                        break

                    else:
                        LOG.debug("Ignoring patch %s for %s as to submit patch type is %s",
                                 str(patch.name), str(original_cbid), str(to_submit_patch_type))

            if patches_to_submit:
                CSSubmissionCable.get_or_create(cs=cs, ids=patch.ids_rule, cbns=patches_to_submit)
            else:
                LOG.debug("No patches to submit for cs %s, patch type %s",
                         cs.name, str(to_submit_patch_type))


        self.submission_index += 1
