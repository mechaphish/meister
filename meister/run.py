from .ti.api import API
from time import sleep
from os import getenv as ENV

def run(url, username, password):
    api = API(url, username, password)
    while True:
        round_n = api.status()['round']
        print "[Meister] Round # %s" % round_n
        binaries = api.binaries(round_n)['binaries']
        sleep(3)
