#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Distutil setup scripts for meister and its requirements."""

# pylint: disable=import-error,no-name-in-module

import os
import os.path
import shutil

from distutils.core import setup

# Setup binary directory, to copy to bin on install
if not os.path.exists('bin'):
    os.makedirs('bin')

# Copy binary scripts
shutil.copyfile('meister/__main__.py', 'bin/meister')

with open('requirements.txt', 'r') as req_file:
    REQUIREMENTS = [r.strip() for r in req_file.readlines() if 'git' not in r]

setup(name='meister',
      version='0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1',
      packages=['meister', 'meister.schedulers'],
      scripts=['bin/meister'],
      install_requires=REQUIREMENTS,
      description='Master component of the Shellphish CRS.',
      url='https://git.seclab.cs.ucsb.edu/cgc/meister')
