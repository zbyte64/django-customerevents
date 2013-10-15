# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

from ..tracker import get_tracker

register = template.Library()


@register.simple_tag
def render_events(*backends):
    tracker = get_tracker()
    #if we don't have an identity then there isn't anything to send
    if not tracker.identity_id:
        return ''
    bts = tracker.flush()
    rendered = list()
    for bt in bts:
        if backends and bt.name not in backends:
            continue
        try:
            payload = bt.render()
        except NotImplementedError:
            pass
        else:
            rendered.append(payload)
    return mark_safe('\n'.join(rendered))
