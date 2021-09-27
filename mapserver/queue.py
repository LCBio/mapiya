from django.conf import settings
from . import models
from collections import deque
import io
import threading
import time
import json
import traceback


def project_worker(queue):
    while queue:
        job = queue.popleft()
        job.status = 'R'
        job.save(update_fields=['status'])
        try:
            job.save_matrix()
            job.status = 'F'
            job.save(update_fields=['status'])
        except Exception:
            info = json.loads(job.info) if job.info else {}
            errors = info.get('errors', [])
            with io.StringIO() as f:
                traceback.print_exc(file=f)
                f.seek(0)
                errors.append(f.read())
            info['errors'] = errors
            job.info = json.dumps(info)
            job.status = 'E'
            job.save(update_fields=['status', 'info'])


def queue_manager():
    while True:
        queue = deque(models.Job.objects.filter(status='Q').order_by('date_init'))
        max_workers = min(settings.QUEUE_WORKERS_COUNT, len(queue))
        workers = [threading.Thread(target=project_worker, args=[queue]) for _ in range(max_workers)]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        time.sleep(settings.QUEUE_MANAGER_TIMEOUT_SECONDS)


threading.Thread(target=queue_manager, daemon=True).start()
