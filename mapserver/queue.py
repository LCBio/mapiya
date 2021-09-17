from django.conf import settings
from . import models
from collections import deque
import io
import threading
import time
import json
import traceback


def map_worker(queue):
    while queue:
        map_model = queue.popleft()
        map_model.status = 'R'
        map_model.save(update_fields=['status'])
        try:
            map_model.save_matrix()
            map_model.status = 'F'
            map_model.save(update_fields=['status'])
        except Exception:
            info = json.loads(map_model.info) if map_model.info else {}
            errors = info.get('errors', [])
            with io.StringIO() as f:
                traceback.print_exc(file=f)
                f.seek(0)
                errors.append(f.read())
            info['errors'] = errors
            map_model.info = json.dumps(info)
            map_model.status = 'E'
            map_model.save(update_fields=['status', 'info'])


def queue_manager():
    while True:
        queue = deque(models.MapModel.objects.filter(status='Q').order_by('date_init'))
        max_workers = min(settings.QUEUE_WORKERS_COUNT, len(queue))
        workers = [threading.Thread(target=map_worker, args=[queue]) for _ in range(max_workers)]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        time.sleep(settings.QUEUE_MANAGER_TIMEOUT_SECONDS)


threading.Thread(target=queue_manager, daemon=True).start()
