# -*- coding: utf-8 -*-
from .tracker import set_tracker


class TrackingMiddleware(object):
    def process_request(self, request):
        self.tracker = set_tracker(request)
        if getattr(request, 'user'):
            if request.user.is_authenticated():
                self.tracker.identify(request.user.pk)
            elif hasattr(request, 'session'):
                self.tracker.identify(request.session.session_key)

    def process_response(self, request, response):
        bound_trackers = self.tracker.flush()
        for bt in bound_trackers:
            bt.async_send()
        return response
