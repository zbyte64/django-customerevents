# -*- coding: utf-8 -*-
from django.template.loader import render_to_string


class BaseBackend(object):
    template_name = None

    def __init__(self, name):
        self.name = name
        super(BaseBackend, self).__init__()

    def get_template(self):
        return [self.template_name]

    def get_context(self, **kwargs):
        return kwargs

    def render(self, context):
        template = self.get_template()
        context = self.get_context(**context)
        return render_to_string(template, context)

    def send(self, identity, properties, aliases, events, request_meta):
        raise NotImplementedError
