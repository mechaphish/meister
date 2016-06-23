#!/usr/bin/env python
# -*- coding: utf-8 -*-

from meister.creators import BaseCreators


class PwnrexCreator(BaseCreators):

    @property
    def jobs(self):
        # check for new replay attack

        out = []

        # for b in crscommon.api.get_all_binaries():
        #     for team in crscommon.api.get_all_teams():
        #         out.append(PwnrexJob(b, b.pcaps(team, crscommon.api.get_current_round())))

        return out
