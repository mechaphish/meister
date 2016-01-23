from ..scheduler import Scheduler
from ..jobs import AFLJob

class AFLScheduler(Scheduler):
    def schedule(self):
        return [ AFLJob('ccf3d301_01') ]
