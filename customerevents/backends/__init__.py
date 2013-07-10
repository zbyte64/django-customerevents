# -*- coding: utf-8 -*-
from threading import local

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


BACKENDS = local()


def get_backend(name):
    return get_backends().get(name)


def get_backends():
    if not hasattr(BACKENDS, 'backends'):
        BACKENDS.backends = dict()
        for key, params in getattr(settings, 'TRACKING_BACKENDS', {}).items():
            kwds = dict(params)
            path = kwds.pop('MODULE')
            kwds['name'] = key
            BACKENDS.backends[key] = load_backend(path, **kwds)
    return BACKENDS.backends


def load_backend(path, **kwds):
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured(('Error importing event tracking backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(**kwds)