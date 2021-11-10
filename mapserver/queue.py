import collections
import io
import threading
import time
import traceback

from django.conf import settings
from django.db import DatabaseError, OperationalError

from . import models


def project_worker(queue):
    while queue:
        job = queue.popleft()
        job.status = 'R'
        job.save(update_fields=['status'])
        try:
            job.run()
            job.status = 'F'
            job.save(update_fields=['status'])
        except [DatabaseError, OperationalError]:
            # TODO: ugly patch to delete running jobs
            pass
        except Exception:
            with io.StringIO() as f:
                traceback.print_exc(file=f)
                f.seek(0)
                job.error = f.read()
            job.status = 'E'
            job.save(update_fields=['status', 'error'])


def queue_manager():
    while True:
        queue = collections.deque(models.Job.objects.filter(status='Q').order_by('date_init'))
        max_workers = min(settings.QUEUE_WORKERS_COUNT, len(queue))
        workers = [threading.Thread(target=project_worker, args=[queue]) for _ in range(max_workers)]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        time.sleep(settings.QUEUE_MANAGER_TIMEOUT_SECONDS)


threading.Thread(target=queue_manager, daemon=True).start()
