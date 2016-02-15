from os import environ as ENV
from farnsworth_client.models import Job

class Scheduler(object):
    def __init__(self):
        # kubemaster_url = "http://{}:{}".format(ENV['KUBERNETS_SERVICE_HOST'], ENV['KUBERNETES_SERVICE_PORT'])
        None

    def schedule(self, worker, cbn, cpus, memory):
        # FIXME: schedule Kubernetes task too
        return (
            Job.find_by(
                worker = worker,
                cbn_id = cbn.id,
            ) or
            Job.create(
                worker = worker,
                cbn_id = cbn.id,
                limit_cpu = cpus,
                limit_memory = memory,
                payload = cbn   # FIXME: is this really necessary?
            )
        )
