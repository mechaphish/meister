#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from farnsworth.models import ChallengeSetFielding, Crash, Exploit, IDSRuleFielding, PovFuzzer2Job, PovTestResult, Team
from peewee import fn, SQL

import meister.creators
from .rex import Vulnerability, BASE_PRIORITY
LOG = meister.creators.LOG.getChild('povfuzzer2')


class PovFuzzer2Creator(meister.creators.BaseCreator):

    @staticmethod
    def _normalize_sort(base, ordered_crashes):
        for p, c in ordered_crashes:
            yield max(base, 100 - p), c

    @property
    def _jobs(self):
        for cs in self.challenge_sets():
            if not cs.has_type2:
                ordered_crashes = cs.crashes.select(Crash.id) \
                                            .where(Crash.kind == Vulnerability.ARBITRARY_READ) \
                                            .order_by(fn.octet_length(Crash.blob).asc())

                for priority, crash in self._normalize_sort(BASE_PRIORITY, enumerate(ordered_crashes)):
                    job = PovFuzzer2Job(cs=cs, payload={'crash_id': crash.id},
                                        request_cpu=1, limit_memory=2048,
                                        limit_time=5 * 60)
                    LOG.debug("Yielding PovFuzzer2Job for %s with crash %s priority %d",
                              cs.name, crash.id, priority)
                    yield (job, priority)
            else:
                # Schedule pov_fuzzers against other teams
                # We will schedule at most 3 exploits
                longest = list(cs.exploits.select(Exploit.crash)
                                          .join(Crash)
                                          .where(Exploit.method == "fuzzer",
                                                 Exploit.reliability > 0,
                                                 Exploit.pov_type == "type2")
                                          .order_by(fn.octet_length(Crash.blob).desc())
                                          .limit(3))

                for team in Team.opponents():
                    target_cs_fld = ChallengeSetFielding.latest(cs, team)

                    if target_cs_fld is not None:   # Are there any CS fielded?
                        target_ids_fld = IDSRuleFielding.latest(cs, team)

                        # See if there are successful PoVs for this
                        # fielded CS and IDS. If yes, no need to
                        # schedule Pov Testing Jobs
                        pov_test_results = PovTestResult.best(target_cs_fld, target_ids_fld)

                        if pov_test_results is None or pov_test_results.num_success < 3:
                            # We do not have any strong PoVs for the
                            # current fielded CS. Schedule 3 pov_fuzzers
                            for exploit in longest:
                                if target_ids_fld is not None:
                                    target_ids_id = target_ids_fld.id
                                else:
                                    target_ids_id = None

                                payload = {'crash_id': exploit.crash.id,
                                           'target_cs_fld': target_cs_fld.id,
                                           'target_ids_fld': target_ids_id}
                                job = PovFuzzer2Job(cs=cs, payload=payload,
                                                    request_cpu=1, limit_memory=2048,
                                                    limit_time=5 * 60)
                                priority = 80
                                LOG.debug("Yielding targeted PovFuzzer2Job for %s with crash %s priority %d team %d",
                                          cs.name, exploit.crash.id, priority, team.id)
                                yield (job, priority)
