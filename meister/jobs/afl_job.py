from .. import Job

class AFLJob(Job):
    def __init__(self, binary_id):
        Job.__init__(4, 1)
        self.binary_id = binary_id
