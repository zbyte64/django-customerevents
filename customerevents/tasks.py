# -*- coding: utf-8 -*-
from celery import task
from customerevents.backends import get_backend


@task
def send_tracking_to_backend(backend_name, **kwargs):
    backend = get_backend(backend_name)
    return backend.send(**kwargs)
