from distutils.core import setup

setup(
    name='meister',
    version='0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1',
    packages=['meister', 'meister.schedulers'],
    scripts=['bin/meister'],
    install_requires=[i.strip() for i in open('requirements.txt').readlines() if 'git' not in i],
    description='Master component of the Shellphish CRS.',
    url='https://git.seclab.cs.ucsb.edu/cgc/meister',
)
