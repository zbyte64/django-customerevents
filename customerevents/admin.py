# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Customer, Alias, Event

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['identity', 'active']
    list_filter = ['active']
admin.site.register(Customer, CustomerAdmin)

class AliasAdmin(admin.ModelAdmin):
    list_display = ['customer', 'identity']
admin.site.register(Alias, AliasAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'timestamp']
    list_filter = ['timestamp', 'name']
    date_hierarchy = 'timestamp'
admin.site.register(Event, EventAdmin)