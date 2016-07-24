#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Distutil setup scripts for meister and its requirements."""

# pylint: disable=import-error,no-name-in-module

import os
import os.path
import shutil

from distutils.core import setup

with open('requirements.txt', 'r') as req_file:
    REQUIREMENTS = [r.strip() for r in req_file.readlines() if 'git' not in r]

setup(name='meister',
      version='0.0.1',
      packages=['meister', 'meister.creators', 'meister.schedulers'],
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': [
              "meister=meister.__main__:main"
          ],
      },
      description='Master component of the Shellphish CRS.',
      url='https://git.seclab.cs.ucsb.edu/cgc/meister')
