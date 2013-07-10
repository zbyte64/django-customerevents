# -*- coding: utf-8 -*-
import json
from customerio import CustomerIO

from .base import BaseBackend


class CustomerIOBackend(BaseBackend):
    template_name = 'customerevents/customerio.html'

    def __init__(self, SITE_ID, API_KEY, **kwargs):
        self.site_id = SITE_ID
        self.connection = CustomerIO(SITE_ID, API_KEY)
        super(CustomerIOBackend, self).__init__(**kwargs)

    def get_context(self, identity, properties, events, **kwargs):
        context = {
            'identify': {
                'id': identity
            },
            'site_id': self.site_id,
            'tracks': list()
        }
        context['identify'].update(properties)
        context['identify'] = json.dumps(context['identify'])
        context.update(kwargs)
        for event_name, event_properties in events:
            context['tracks'].append((event_name, json.dumps(event_properties)))
        return context

    def send(self, identity, properties, aliases, events):
        self.connection.identify(id=identity, **properties)
        for event_name, event_properties in events:
            self.connection.track(name=event_name, **event_properties)
