#!/usr/bin/env python

import random
from farnsworth.models import (ChallengeBinaryNode,
                               ChallengeSet,
                               ChallengeSetSubmissionCable,
                               IDSRule)
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self):
        self.patch_submission_order = None
        self.submission_index = 0
        self.available_patch_types = set()

    def run(self, current_round=None, random_submit=False):
        if (current_round % 2) == 0:
            # to_submit_patch_type = None
            # to_submit_patch_types = None
            # submit_pt_index = None
            #if self.patch_submission_order is not None:
            #    if self.submission_index >= (len(self.patch_submission_order) - 2):
            #            self.submission_index = 0
            #    to_submit_patch_types = self.patch_submission_order[self.submission_index:]
            #    self.submission_index += 1
            #submit_pt_index = 0

            for cs in ChallengeSet.fielded_in_round():
                curr_patch_types = set(cs.cbns_by_patch_type().keys())
                to_submit_patch_type = None
                if self.patch_submission_order is None or \
                        not (curr_patch_types <= self.available_patch_types):
                    self.available_patch_types = curr_patch_types
                    all_patch_types = map(lambda x: str(x), list(cs.cbns_by_patch_type().keys()))
                    self.patch_submission_order = all_patch_types * 1000
                    self.submission_index = 0
                    # to_submit_patch_types = self.patch_submission_order[self.submission_index:]
                    # self.submission_index += 1

                # if submit_pt_index >= len(to_submit_patch_types):
                #    submit_pt_index = 0

                # if submit_pt_index < len(to_submit_patch_types):
                #    to_submit_patch_type = to_submit_patch_types[submit_pt_index]

                # submit_pt_index += 1
                if self.submission_index >= len(self.patch_submission_order):
                    self.submission_index = 0
                if self.submission_index < len(self.patch_submission_order):
                    to_submit_patch_type = self.patch_submission_order[self.submission_index]
                self.submission_index += 1
                print cs.name, to_submit_patch_type
                # import ipdb; ipdb.set_trace()

                for cbn in cs.cbns_original:
                    for patch in cbn.unsubmitted_patches:
                        original_cbid = cbn.name
                        if patch.patch_type is not None and (to_submit_patch_type is None or
                                                             to_submit_patch_type == str(patch.patch_type)):
                            LOG.info("Submitting patch %s for %s", patch.name, original_cbid)
                            CSSB = ChallengeSetSubmissionCable
                            CSSB.get_or_create(cs=cs, cbns=patch, ids=patch.ids_rule)
                            # FIXME: we submit only one patch type at onceon ro
                            break

                        else:
                            LOG.info("Ignoring patch %s for %s as to submit patch type is %s",
                                     str(patch.name), str(original_cbid), str(to_submit_patch_type))
