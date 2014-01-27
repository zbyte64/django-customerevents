from threading import local

from .backends import get_backends
from .tasks import send_tracking_to_backend, send_tracking_to_backends


SESSION = local()


def get_tracker(request=None):
    if hasattr(SESSION, 'tracker'):
        if request:
            if SESSION.tracker.request:
                assert SESSION.tracker.request == request
            else:
                SESSION.tracker.set_request(request)
        return SESSION.tracker
    return set_tracker(request)


def set_tracker(request=None):
    SESSION.tracker = Tracker(get_backends(), request=request)
    return SESSION.tracker


def unset_tracker():
    if hasattr(SESSION, 'tracker'):
        delattr(SESSION, 'tracker')


class Tracker(object):
    def __init__(self, backends, request=None):
        self.backends = backends
        self.identity = dict()
        self.identity_id = None
        self.aliases = set()
        self.events = list()
        self._closed = False
        self.set_request(request)

    def set_request(self, request):
        self.request = request
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

    def identify(self, id, properties=None):
        self._check_open()
        if self.identity_id is not None and id != self.identity_id:
            self.alias(self.identity_id, id)
        else:
            self.identity_id = id
        if properties:
            self.identity.update(properties)

    def set(self, key, value):
        self._check_open()
        self.identity[key] = value

    def event(self, name, properties):
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

    @property
    def data(self):
        return self.tracker.to_pystruct()

    def render(self):
        '''
        Returns html/js for inclusion in a client facing page
        '''
        self._check_sent()
        try:
            ret = self.backend.render(self.data)
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
        return self.backend.send(**self.data)

    def async_send(self):
        '''
        Schedules tracking to be sent by a task worker
        '''
        self._check_sent()
        self.sent = True
        kwargs = self.tracker.to_pystruct()
        kwargs['backend_name'] = self.backend.name
        return send_tracking_to_backend.delay(**kwargs)


def identify(identity, _=None, **properties):
    tracker = get_tracker()
    return tracker.identify(identity, _ or properties)


def send_event(name, _=None, **properties):
    tracker = get_tracker()
    return tracker.event(name, _ or properties)


def flush():
    tracker = get_tracker()
    if not tracker.has_data():
        return
    bound_trackers = tracker.flush()
    backend_names = [bt.backend.name for bt in bound_trackers]
    kwargs = tracker.to_pystruct()
    unset_tracker()
    return send_tracking_to_backends.delay(backend_names, **kwargs)
