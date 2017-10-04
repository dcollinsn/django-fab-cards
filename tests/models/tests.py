from django.test import TestCase

from magic_cards.models import Card
from magic_cards.utils.import_cards import import_cards


class ImportScriptTests(TestCase):
    def test_long_card_name(self):
        """
        The longest card name can be successfully imported and stored fully in the database.
        """
        import_cards(["UNH"])

        longest_name = "Our Market Research Shows That Players Like Really Long Card Names " \
                       "So We Made this Card to Have the Absolute Longest Card Name Ever Elemental"
        longest_name_card = Card.objects.get(name=longest_name)
        self.assertEqual(longest_name_card.name, longest_name)
        # SQLite does not actually enforce the length of a VARCHAR, but Django will validate
        # if we call full_clean.
        longest_name_card.full_clean()

    def test_planeswalker_loyalty(self):
        import_cards(["AVR"])

        tamiyo = Card.objects.get(name="Tamiyo, the Moon Sage")
        self.assertEqual(tamiyo.loyalty, 4)

        tracker = Card.objects.get(name="Ulvenwald Tracker")
        self.assertIsNone(tracker.loyalty)
