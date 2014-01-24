# -*- coding: utf-8 -*-
import json
from ..models import Customer, Alias, Event
from .base import BaseBackend


def update_alias(customer, alias):
    obj, created = Alias.objects.get_or_create(identity=alias,
        defaults={"customer": customer})
    if not created and obj.customer != customer:
        obj.customer = customer
        obj.save()
    return obj


class ModelBackend(BaseBackend):
    def render(self, context):
        #there is currently no public api to execute this
        raise NotImplementedError

    def get_active_customer(self, identity, aliases):
        customer, created = Customer.objects.get_or_create(identity=identity)
        if not customer.active:
            customer = Customer.objects.get(aliases__customer=customer)
        return customer

    def send(self, identity, properties, aliases, events, request_meta):
        customer = self.get_active_customer(identity, aliases)

        if aliases:
            left_over_aliases = set(aliases)
            merged_properties = dict()
            from_customers = Customer.objects.filter(identity__in=aliases).exclude(pk=customer.pk)
            for from_customer in from_customers:
                #move events
                from_customer.events.all().update(customer=customer)
                #add alias
                update_alias(customer, from_customer.identity)
                left_over_aliases.remove(from_customer.identity)
                merged_properties.update(from_customer.properties)
                from_customer.active = False
                from_customer.save()
            #create mising aliases and move existing
            for alias in left_over_aliases:
                update_alias(customer, alias)
            Alias.objects.filter(customer__in=from_customers).update(customer=customer)
            #update properties
            merged_properties.update(customer.properties)
            customer.properties = merged_properties

        if properties:
            if isinstance(customer.properties, basestring):
                if customer.properties:
                    try:
                        customer.properties = json.dumps(customer.properties)
                    except ValueError:
                        customer.properties = dict()
                else:
                    customer.properties = dict()
            customer.properties.update(properties)
            customer.save()

        for event_name, event_properties in events:
            Event.objects.create(customer=customer,
                                 name=event_name,
                                 properties=event_properties)