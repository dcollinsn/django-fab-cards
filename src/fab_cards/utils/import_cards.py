import io
import json
import zipfile
from contextlib import closing

import requests
from django.db import transaction

from fab_cards.models import Card, Printing, Set

API_URL = "https://fabdb.net/api/cards"


def fetch_data():
    card_data = []
    page = 1
    while True:
        r = requests.get(API_URL + "?per_page=100&page=" + str(page))
        r.raise_for_status()
        page_data = r.json()
        card_data.extend(page_data['data'])
        if page_data['meta']['current_page'] == page_data['meta']['last_page']:
            break
        page += 1

    return card_data


class ModelCache(dict):
    def get_or_create(self, model, field, value, **kwargs):
        """
        Retrieves object of class `model` with lookup key `value` from the cache. If not found,
        creates the object based on `field=value` and any other `kwargs`.

        Returns a tuple of `(object, created)`, where `created` is a boolean specifying whether an
        `object` was created.
        """
        result = self[model].get(value.lower())
        created = False
        if not result:
            kwargs[field] = value
            result = model.objects.create(**kwargs)
            self[model][value.lower()] = result
            created = True
        return result, created


def parse_data(all_data):
    # Load supertypes, types, and subtypes into memory
    cache = ModelCache()
    # Load relevant sets into memory
    cache[Set] = {obj.code.lower(): obj for obj in Set.objects.all()}

    # Process the data set-by-set
    for card_data in all_data:
        # Get or create the card
        defaults = {'name': card_data['name']}
        if 'text' in card_data:
            defaults['text'] = card_data['text']
        if 'keywords' in card_data:
            defaults['keywords'] = ' '.join(card_data['keywords'])
        if 'rarity' in card_data:
            defaults['rarity'] = card_data['rarity']
        if 'stats' in card_data:
            defaults.update(card_data['stats'])
        card, card_created = Card.objects.update_or_create(
            identifier=card_data['identifier'],
            defaults=defaults,
        )


        # Create the printings
        for printing in card_data['printings']:

            # Create the set
            set_code = printing['sku']['set']['id']
            set_name = printing['sku']['set']['name']
            card_set, set_created = cache.get_or_create(Set, 'code', set_code, name=set_name)

            printing_sku = printing['sku']['sku']
            printing_kwargs = {
                'card': card,
                'set': card_set,
                'rarity': printing['rarity'],
                'finish': printing['sku']['finish'],
                'printing_id': printing['id'],
                'image_url': printing['image'],
            }
            Printing.objects.update_or_create(
                sku=printing_sku,
                defaults=printing_kwargs,
            )


@transaction.atomic
def import_cards():
    all_data = fetch_data()
    parse_data(all_data)


if __name__ == "__main__":
    import_cards()
