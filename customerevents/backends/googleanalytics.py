# -*- coding: utf-8 -*-
from pyga.requests import Tracker, Event, Session, Visitor

from django.contrib.sites.models import Site

from .base import BaseBackend


class GoogleAnalyticsBackend(BaseBackend):
    template_name = 'customerevents/google_analytics.html'

    def __init__(self, WEB_ID, EVENT_CATEGORY='generic', **kwargs):
        self.web_id = WEB_ID
        self.event_category = EVENT_CATEGORY
        super(GoogleAnalyticsBackend, self).__init__(**kwargs)

    def get_context(self, **kwargs):
        context = {
            'web_id': self.web_id,
            'category': self.event_category
        }
        context.update(kwargs)
        return context

    def send(self, identity, properties, aliases, events, request_meta):
        host_name = (request_meta.get('HTTP_HOST') or
                     Site.objects.get_current().domain)
        tracker = Tracker(self.web_id, host_name)
        visitor = Visitor()
        visitor.unique_id = abs(hash(identity)) >> 33
        visitor.extract_from_server_meta(request_meta)
        session = Session()
        for event_name, event_properties in events:
            event = Event(category=self.event_category, action=event_name)
            tracker.track_event(event, session, visitor)
