#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database job creator.

Create jobs from the persistent database.
"""

import meister.creators
from farnsworth.models.job import Job, to_job_type

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
            yield to_job_type(job)
