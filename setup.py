from distutils.core import setup

setup(
    name='meister',
    version='0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1',
    packages=['meister', 'meister.schedulers'],
    scripts=['bin/meister'],
    install_requires=[
        'requests',
        'python-dotenv',
        'crscommon',
        'farnsworth-client',
        'pykube',
        # test dependencies
        'responses',
        'nose>=1.3.7',
        'nose-timer>=0.5.0',
        'coverage>=4.0.3',
    ],
    description='Master component of the Shellphish CRS.',
    url='https://git.seclab.cs.ucsb.edu/cgc/meister',
)
