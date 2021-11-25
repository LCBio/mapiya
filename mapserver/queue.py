import io
import threading
import time
import traceback
import collections

from django.conf import settings

from . import models


def queue_worker(queue):
    while queue:
        job = queue.popleft()
        job.status = 'R'
        job.save(update_fields=['status'])
        try:
            job.run()
        except Exception:
            with io.StringIO() as f:
                traceback.print_exc(file=f)
                f.seek(0)
                job.error = f.read()
            job.status = 'E'
            job.save(update_fields=['status', 'error'])


def queue_manager():
    queue = collections.deque()
    while True:
        jobs = models.Job.objects.filter(status='S').order_by('date_init')
        queue.extend(jobs)
        jobs.update(status='Q')

        max_workers = min(settings.QUEUE_WORKERS_COUNT, len(queue))
        workers = [
            threading.Thread(target=queue_worker, args=[queue], name=f'QueueWorker-{index}')
            for index in range(max_workers)
        ]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        time.sleep(settings.QUEUE_MANAGER_TIMEOUT_SECONDS)


threading.Thread(target=queue_manager, name='Queue manager', daemon=True).start()
