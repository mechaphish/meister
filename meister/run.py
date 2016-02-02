from time import sleep
from os import environ as ENV
from .cgc_client.api import API as CgcAPI
from .scheduler import Scheduler
from .farnsworth_client import API as ProfAPI

def run():
    cgc = CgcAPI(ENV['CGC_API_URL'], ENV['CGC_API_USER'], ENV['CGC_API_PASS'])
    prof_url = "http://{}:{}".format(ENV['FARNSWORTH_SERVICE_HOST'], ENV['FARNSWORTH_SERVICE_PORT'])
    prof = ProfAPI(prof_url)
    while True:
        round_n = cgc.status()['round']
        print "[Meister] Round # %s" % round_n
        binaries = cgc.binaries(round_n)['binaries']
        sleep(3)
