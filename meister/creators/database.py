#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database job creator.

Create jobs from the persistent database.
"""

import meister.creators
from farnsworth.models.job import Job, AFLJob, DrillerJob, RexJob, PatcherexJob, TesterJob

LOG = meister.creators.LOG.getChild('database')


class DatabaseCreator(meister.creators.BaseCreator):
    """
    Create jobs from jobs that are in the database but not yet started.

    Fetching jobs from the database is required for example if the meister is
    being restarted.
    """
    @property
    def jobs(self):
        """Yield every job that is stored in the database."""
        for job in Job.select(id, ).where(Job.started_at.is_null(True)):
            # Directly setting the __class__ member only works because our
            # job subclasses do not add extra instance variables, but only
            # member functions that we are calling.
            if job.worker == 'afl':
                job.__class__ = AFLJob
            elif job.worker == 'driller':
                job.__class__ = DrillerJob
            elif job.worker == 'rex':
                job.__class__ = RexJob
            elif job.worker == 'patcherex':
                job.__clas__ = PatcherexJob
            elif job.worker == 'tester':
                job.__class__ = TesterJob
            yield job
