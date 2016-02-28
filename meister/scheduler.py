from .kube_config import kube_config
from pykube.http import HTTPClient
from pykube.objects import ReplicationController
from requests.exceptions import HTTPError
from os import environ as ENV

from farnsworth_client.models import Job

class Scheduler(object):
    def __init__(self):
        self.api = HTTPClient(kube_config)
        None

    def schedule(self, worker, cbn, cpus, memory):
        job = (
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
        self.schedule_kube_controller(job, cpus, memory)
        return job

    def schedule_kube_controller(self, job, cpus, memory):
        name = "worker-{}".format(job.id)
        config = {
            'metadata': {'name': name},
            'spec': {
                'replicas': 1,
                'selector': {'job_id': str(job.id)},
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'worker',
                            'worker': job.worker,
                            'job_id': str(job.id), # for identification
                        },
                        'name': name
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': name,
                                'image': 'worker',
                                'resources': {
                                    'requests': {
                                        'cpu': str(cpus),
                                        'memory': "{}Gi".format(memory)
                                    }
                                },
                                'env': [
                                    {'name': "JOB_ID", 'value': str(job.id)}
                                ]
                            }
                        ]
                    }
                }
            }
        }
        try:
            if ENV['KUBERNETES_SERVICE_HOST']:
                ReplicationController(self.api, config).create()
        except HTTPError as e:
            if e.response.status_code == 409:
                print "Already scheduled"
            else:
                raise e
