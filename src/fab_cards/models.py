from __future__ import unicode_literals

import random

from django.db import models
from six import python_2_unicode_compatible
from django_light_enums import enum


@python_2_unicode_compatible
class NameMixin(object):
    def __str__(self):
        return self.name


class Card(NameMixin, models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)

    keywords = models.CharField(max_length=255, null=True, blank=True)

    attack = models.CharField(max_length=8, null=True, blank=True)
    defense = models.CharField(max_length=8, null=True, blank=True)
    resource = models.CharField(max_length=8, null=True, blank=True)
    cost = models.CharField(max_length=8, null=True, blank=True)
    intellect = models.CharField(max_length=8, null=True, blank=True)
    life = models.CharField(max_length=8, null=True, blank=True)
    rarity = models.CharField(max_length=2, null=True, blank=True)

    @property
    def needs_disambig(self):
        return self.identifier.split('-')[-1] in ('red', 'yellow', 'blue') and self.resource

    @property
    def color_bar(self):
        if self.resource:
            return ('red', 'yellow', 'blue')[int(self.resource)-1]
        return False

    def __str__(self):
        if self.needs_disambig:
            return f"{self.name} ({self.color_bar})"
        return self.name


class Set(NameMixin, models.Model):
    name = models.CharField(max_length=63, unique=True)
    code = models.CharField(max_length=8, unique=True)


class PrintingQuerySet(models.QuerySet):
    def random(self, num):
        num = int(num)
        printing_ids = set(self.values_list('id', flat=True))
        random_ids = random.sample(printing_ids, num)
        return self.filter(id__in=random_ids)


@python_2_unicode_compatible
class Printing(models.Model):
    objects = PrintingQuerySet.as_manager()

    card = models.ForeignKey('Card',
                             on_delete=models.CASCADE,
                             related_name='printings')
    set = models.ForeignKey('Set',
                            on_delete=models.CASCADE,
                            related_name='printings')
    sku = models.CharField(max_length=32, unique=True)
    rarity = models.CharField(max_length=2, null=True, blank=True)
    finish = models.CharField(max_length=32, null=True, blank=True)
    printing_id = models.PositiveIntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=256, null=True, blank=True)

    language = models.CharField(max_length=2, default="en")

    def __str__(self):
        return '{} ({})'.format(self.card, self.set.code)

