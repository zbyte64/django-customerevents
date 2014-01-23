# -*- coding: utf-8 -*-
import json
from KISSmetrics import KM

from .base import BaseBackend


class KissMetricsBackend(BaseBackend):
    template_name = 'customerevents/kissmetrics.html'

    def __init__(self, API_KEY, **kwargs):
        self.connection = KM(API_KEY)
        self.api_key = API_KEY
        super(KissMetricsBackend, self).__init__(**kwargs)

    def get_context(self, identity, properties, events, **kwargs):
        context = {
            'identify': identity,
            'properties': json.dumps(properties),
            'record': list(),
            'api_key': self.api_key,
        }
        context.update(kwargs)
        for event_name, event_properties in events:
            context['record'].append((event_name, json.dumps(event_properties)))
        return context

    def send(self, identity, properties, aliases, events, request_meta):
        self.connection.identify(identity)
        for alias in aliases:
            self.connection.alias(identity, alias)
        if properties:
            self.connection.set(properties)
        for event_name, event_properties in events:
            self.connection.record(event_name, event_properties)
