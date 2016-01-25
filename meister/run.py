from time import sleep
from .ti.api import API
from .scheduler import Scheduler

def run(url, username, password):
    api = API(url, username, password)
    while True:
        round_n = api.status()['round']
        print "[Meister] Round # %s" % round_n
        binaries = api.binaries(round_n)['binaries']
        Scheduler().schedule("worker-test")
        sleep(3)
