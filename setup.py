#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Distutil setup scripts for meister and its requirements."""

# pylint: disable=import-error,no-name-in-module

import os
import os.path
import shutil

from distutils.core import setup

REQUIREMENTS, DEPENDENCIES = [], []
with open('requirements.txt', 'r') as req_file:
    for r in req_file.readlines():
        r_ = r.strip()
        if r_.startswith('git+'):
            DEPENDENCIES.append(r_)
            # FIXME: We are discarding the version number here
            REQUIREMENTS.append(r_.rsplit("egg=", 1)[1].rsplit("-", 1)[0])
        else:
            REQUIREMENTS.append(r_)

setup(name='meister',
      version='0.0.1',
      packages=['meister', 'meister.creators', 'meister.schedulers'],
      install_requires=REQUIREMENTS,
      dependency_links=DEPENDENCIES,
      entry_points={
          'console_scripts': [
              "meister=meister.__main__:main"
          ],
      },
      description='Master component of the Shellphish CRS.',
      url='https://git.seclab.cs.ucsb.edu/cgc/meister')
