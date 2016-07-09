#!/usr/bin/env python

import random
from farnsworth.models import ChallengeBinaryNode, IDSRule
from meister.cgc.tierror import TiError
import meister.log

LOG = meister.log.LOG.getChild('cbsubmitter')

class CBSubmitter(object):

    def __init__(self, cgc):
        self._cgc = cgc
        self.submitted_bins = {}
        self.submission_history = {}

    def run(self, current_round, random_submit=False):
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (current_round % 2) == 1:
            no_submissions = True
            for cbn in ChallengeBinaryNode.roots():
                # submitted_ids = cbn.cs.ids_rules.where(IDSRule.submitted_at.is_null(True))
                # # dont' submit CB that has IDS active
                # if len(submitted_ids) > 0:
                #     continue
                # # submit patches for 50% of binaries, so we can test IDs on the other 50%
                # if random_submit and (random.randint(0,1) == 0):
                #     continue

                for patch in cbn.unsubmitted_patches:
                    cs_key = str(cbn.cs.name)
                    patch_val = str(patch.patch_type)
                    if cs_key not in self.submitted_bins:
                        if patch_val not in self.submitted_bins.values():
                            if (cs_key not in self.submission_history) or \
                                    (patch_val not in self.submission_history[cs_key]):
                                LOG.info("Submitting patch %s for %s on round %s",
                                         patch.name, cbn.name, current_round)
                                try:
                                    self._cgc.uploadRCB(str(cbn.cs.name),
                                                        (str(cbn.name), str(patch.blob)))
                                    patch.submit()
                                    no_submissions = False
                                    self.submitted_bins[cs_key] = patch_val
                                    # FIXME: we submit only one patch type at once
                                    break
                                except TiError as e:
                                    LOG.error("Submission error: %s", e.message)
                            else:
                                LOG.info("Ignoring patch type %s for %s as we already submitted in previous round",
                                         patch_val, cs_key)
                        else:
                            LOG.info("Ignoring patch type %s as we already submitted that for a different CS",
                                     str(patch.patch_type))
                    else:
                        LOG.info("Ignoring patch %s for %s as we already submitted a patch type %s", str(patch.name),
                                 str(cbn.name), self.submitted_bins[cs_key])
            if no_submissions:
                for cs_name, patch_type in self.submitted_bins.iteritems():
                    if cs_name not in self.submission_history:
                        self.submission_history[cs_name] = set()
                    self.submission_history[cs_name].add(patch_type)
                self.submitted_bins = {}
