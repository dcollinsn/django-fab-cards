from django.core.management import BaseCommand
import inflect

from fab_cards.models import Card, Printing, Set
from fab_cards.utils.import_cards import import_cards


class Command(BaseCommand):
    help = 'Imports data from FABDB into your local database.'

    def handle(self, *args, **options):
        models_to_track = [Set, Card, Printing]
        initial = {model: model.objects.count() for model in models_to_track}

        p = inflect.engine()

        self.stdout.write("Beginning import of all cards.")
        import_cards()
        self.stdout.write("Import complete.")

        final = {model: model.objects.count() for model in models_to_track}
        status_strings = [
            p.inflect(
                "{0} new num({0},)plural_noun({1})".format(final[model] - initial[model], model._meta.object_name))
            for model in models_to_track
        ]
        self.stdout.write("Added {}.".format(p.join(status_strings)))
