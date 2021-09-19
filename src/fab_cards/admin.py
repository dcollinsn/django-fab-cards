from django.contrib import admin

from .models import Card, Set, Printing


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Printing)
class PrintingAdmin(admin.ModelAdmin):
    search_fields = ['card__name']
    list_filter = ['set']

