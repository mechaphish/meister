from ..scheduler import Scheduler

class AFLScheduler(Scheduler):
    def schedule(self, cbn, cpus, memory):
        worker = 'afl'
        return super(AFLScheduler, self).schedule(worker, cbn, cpus, memory)
