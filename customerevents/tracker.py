from threading import local

from .backends import get_backends
from .tasks import send_tracking_to_backend, send_tracking_to_backends


SESSION = local()


def get_tracker(request=None):
    if hasattr(SESSION, 'tracker'):
        if request:
            assert SESSION.tracker.request == request
        return SESSION.tracker

    return Tracker(get_backends(), request=request)


def set_tracker(request=None):
    SESSION.tracker = Tracker(get_backends(), request=request)
    return SESSION.tracker


class Tracker(object):
    def __init__(self, backends, request=None):
        self.backends = backends
        self.request = request
        self.identity = dict()
        self.identity_id = None
        self.aliases = set()
        self.events = list()
        self._closed = False

        self.request_meta = dict()
        if self.request:
            for key, value in request.META.items():
                if isinstance(value, basestring):
                    self.request_meta[key] = value

    def to_pystruct(self):
        return {
            'identity': self.identity_id,
            'properties': self.identity,
            'aliases': self.aliases,
            'events': self.events,
            'request_meta': self.request_meta,
        }

    def close(self):
        self._closed = True

    def _check_open(self):
        return
        assert self._closed is False, 'Tracker object is closed'

    def has_data(self):
        if not self.identity_id:
            return False
        return bool(self.aliases) or bool(self.events) or bool(self.identity)

    def identify(self, id, **properties):
        self._check_open()
        if self.identity_id is not None and id != self.identity_id:
            self.alias(self.identity_id, id)
        else:
            self.identity_id = id
        self.identity.update(properties)

    def set(self, key, value):
        self._check_open()
        self.identity[key] = value

    def event(self, name, **properties):
        self._check_open()
        self.events.append((name, properties))

    def alias(self, from_id, to_id):
        self._check_open()
        assert self.identity_id == from_id
        self.aliases.add(from_id)
        self.identity_id = to_id

    def flush(self):
        self.close()
        if not hasattr(self, 'bound_trackers'):
            self.bound_trackers = list()
            if self.identity_id:
                for backend in self.backends.values():
                    self.bound_trackers.append(BoundTracking(self, backend))
            elif self.events:
                print 'Events found for no identity'
        return [tracker for tracker in self.bound_trackers if not tracker.sent]


class BoundTracking(object):
    def __init__(self, tracker, backend):
        self.tracker = tracker
        self.backend = backend
        self.sent = False

    def _check_sent(self):
        assert self.sent is False, 'Tracker is already sent'

    def render(self):
        '''
        Returns html/js for inclusion in a client facing page
        '''
        self._check_sent()
        try:
            ret = self.backend.render(self.tracker.to_pystruct())
        except NotImplementedError:
            raise
        else:
            self.sent = True
            return ret

    def send(self):
        '''
        Directly notifies the backend of the tracked analytics
        '''
        self._check_sent()
        self.sent = True
        return self.backend.send(**self.tracker.to_pystruct())

    def async_send(self):
        '''
        Schedules tracking to be sent by a task worker
        '''
        self._check_sent()
        self.sent = True
        kwargs = self.tracker.to_pystruct()
        kwargs['backend_name'] = self.backend.name
        return send_tracking_to_backend.delay(**kwargs)


def identify(identity, **properties):
    tracker = get_tracker()
    return tracker.identify(identity, **properties)


def send_event(name, **properties):
    tracker = get_tracker()
    return tracker.event(name, **properties)


def flush():
    tracker = get_tracker()
    bound_trackers = tracker.flush()
    backend_names = [bt.backend.name for bt in bound_trackers]
    kwargs = tracker.to_pystruct()
    return send_tracking_to_backends.delay(backend_names, **kwargs)

