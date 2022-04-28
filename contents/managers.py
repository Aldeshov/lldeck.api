from django.db import models


class CardTemplateManager(models.Manager):

    def create_from_card(self, card):
        return self.create(name=card.name, deck=card.deck)
