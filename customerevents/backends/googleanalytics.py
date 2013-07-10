# -*- coding: utf-8 -*-
from pyga.requests import Tracker, Event, Session, Visitor

from django.contrib.sites.models import get_current_site

from .base import BaseBackend


class GoogleAnalyticsBackend(BaseBackend):
    template_name = 'customerevents/google_analytics.html'

    def __init__(self, WEB_ID, EVENT_CATEGORY='', **kwargs):
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

    def send(self, identity, properties, aliases, events, http_meta=None):
        site = get_current_site()
        tracker = Tracker(self.web_id, site.domain)
        visitor = Visitor()
        if http_meta:
            visitor.extract_from_server_meta(http_meta)
        visitor.unique_id = identity
        session = Session()
        for event_name, event_properties in events:
            event = Event(category=self.event_category, action=event_name)
            tracker.track_event(event, session, visitor)
