# -*- coding: utf-8 -*-
import logging
from celery import task
from customerevents.backends import get_backend


COOL_DOWN = 60 * 5  # 5 minutes before retrying


@task
def send_tracking_to_backend(backend_name, **kwargs):
    backend = get_backend(backend_name)
    return backend.send(**kwargs)


@task
def send_tracking_to_backends(backend_names, **kwargs):
    results = list()
    for backend_name in backend_names:
        backend = get_backend(backend_name)
        try:
            results.append(backend.send(**kwargs))
        except:
            logging.exception('Failed to send tracking to backend: %s; Rescheduling backend tracking' % backend_name)
            send_tracking_to_backend.apply_async(countdown=COOL_DOWN,
                                                 args=[backend_name],
                                                 kwargs=kwargs)
    return results
