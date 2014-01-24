# -*- coding: utf-8 -*-
import json
from KISSmetrics import KM

from .base import BaseBackend


def normalize_name(name):
    '''
    KissMetrics likes human readable names, not keywords.
    '''
    return name.replace('.', ' ')


def normalize_identity(identity, aliases, properties):
    '''
    If the customer has an email we use that as their identity.
    This may obviously change from one use case to another so this should be
    configurable.
    '''
    if properties.get('email'):
        aliases.add(identity)
        identity = properties['email']
    return identity, aliases, properties


class KissMetricsBackend(BaseBackend):
    template_name = 'customerevents/kissmetrics.html'

    def __init__(self, API_KEY, **kwargs):
        self.connection = KM(API_KEY)
        self.api_key = API_KEY
        super(KissMetricsBackend, self).__init__(**kwargs)

    def get_context(self, identity, aliases, properties, events, **kwargs):
        identity, aliases, properties = normalize_identity(identity, aliases, properties)
        context = {
            'identify': identity,
            'properties': json.dumps(properties),
            'record': list(),
            'api_key': self.api_key,
            'aliases': aliases,
        }
        context.update(kwargs)
        for event_name, event_properties in events:
            context['record'].append((normalize_name(event_name),
                                      json.dumps(event_properties)))
        return context

    def send(self, identity, properties, aliases, events, request_meta):
        identity, aliases, properties = normalize_identity(identity, aliases, properties)
        self.connection.identify(identity)
        for alias in aliases:
            self.connection.alias(identity, alias)
        if properties:
            self.connection.set(properties)
        for event_name, event_properties in events:
            self.connection.record(normalize_name(event_name),
                                   event_properties)
