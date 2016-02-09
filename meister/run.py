from time import sleep
from os import environ as ENV
from .cgc_client.api import API as CgcAPI
from .schedulers import AFLScheduler
from farnsworth_client.api import API as ProfAPI
from farnsworth_client.models import ChallengeBinaryNode

def run():
    cgc = CgcAPI(ENV['CGC_API_URL'], ENV['CGC_API_USER'], ENV['CGC_API_PASS'])
    prof_url = "http://{}:{}".format(ENV['FARNSWORTH_SERVICE_HOST'], ENV['FARNSWORTH_SERVICE_PORT'])
    ProfAPI.init(prof_url)

    while True:
        round_n = cgc.status()['round']
        print "[Meister] Round # %s" % round_n
        binaries = cgc.binaries(round_n)['binaries']
        sleep(3)
