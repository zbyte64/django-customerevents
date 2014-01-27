# -*- coding: utf-8 -*-
import datetime
from django.utils.timezone import utc

from .tracker import set_tracker, unset_tracker
from .tasks import send_tracking_to_backends


class TrackingMiddleware(object):
    def process_request(self, request):
        self.tracker = set_tracker(request)
        if getattr(request, 'user'):
            if request.user.is_authenticated():
                props = self.get_user_properties(request.user)
                self.tracker.identify('userid:%s' % request.user.pk, props)
            elif hasattr(request, 'session') and request.session.session_key:
                self.tracker.identify('session:%s' % request.session.session_key)

    def process_response(self, request, response):
        if hasattr(self, 'tracker') and self.tracker.has_data():
            bound_trackers = self.tracker.flush()
            backend_names = [bt.backend.name for bt in bound_trackers]
            kwargs = self.tracker.to_pystruct()
            send_tracking_to_backends.delay(backend_names, **kwargs)
        unset_tracker()
        return response

    def get_user_properties(self, user):
        props = dict()
        if hasattr(user, 'email'):
            props['email'] = user.email
        if hasattr(user, 'get_full_name'):
            props['name'] = user.get_full_name()
        if hasattr(user, 'date_joined'):
            props['created_at'] = unix_time(user.date_joined)
        return props


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=utc)
    delta = dt - epoch
    return delta.total_seconds()