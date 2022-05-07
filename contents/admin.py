from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from contents.forms import DeckTemplateCreationForm
from contents.models import DeckTemplate, CardTemplate, Deck, Card, CardTemplateFrontContent, CardTemplateBackContent, \
    CardFrontContent, CardBackContent, DeckTag


@admin.register(DeckTemplate)
class DeckTemplateAdmin(admin.ModelAdmin):
    """
    Custom deck template admin page
    Allows creating from some existing deck
    Shows some extra information
    """
    list_display = ('name', 'date_created', 'cards_count')
    search_fields = ('name',)
    exclude = ('downloaded', 'liked', 'disliked')
    filter_horizontal = ()

    def save_related(self, request, form, formsets, change):
        if change or form.instance.creator_id:
            return super(DeckTemplateAdmin, self).save_related(request, form, formsets, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'creator', 'date_created', 'date_updated', 'cards_count', 'downloads', 'likes', 'dislikes'
        return super(DeckTemplateAdmin, self).get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            return DeckTemplateCreationForm
        return super(DeckTemplateAdmin, self).get_form(request, obj, change, **kwargs)


class CardTemplateFrontContentInline(admin.StackedInline):
    model = CardTemplateFrontContent
    verbose_name = "Front of the card template"

    def get_min_num(self, request, obj=None, **kwargs):
        return 1

    def get_max_num(self, request, obj=None, **kwargs):
        return self.get_min_num(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


class CardTemplateBackContentInline(admin.StackedInline):
    model = CardTemplateBackContent
    verbose_name = "Back of the card template"

    def get_min_num(self, request, obj=None, **kwargs):
        return 1

    def get_max_num(self, request, obj=None, **kwargs):
        return self.get_min_num(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin, DynamicArrayMixin):
    """
    Custom card template admin page
    Allows full card edit (+ front and back)
    """
    inlines = (CardTemplateFrontContentInline, CardTemplateBackContentInline)
    list_display = ('name', 'deck')
    ordering = ('deck',)
    filter_horizontal = ()

    class Media(DynamicArrayMixin.Media):
        css = {
            'all': DynamicArrayMixin.Media.css.get('all') + ('css/custom_admin.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'deck',
        return super(CardTemplateAdmin, self).get_readonly_fields(request, obj)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    """
    Custom user's (profile's) deck admin page
    Allows creating from some existing templates
    Shows some extra information
    """
    list_display = ('name', 'profile', 'favorite', 'cards_count')
    filter_horizontal = ()

    def save_related(self, request, form, formsets, change):
        if change or not form.fields.get('template'):
            return super(DeckAdmin, self).save_related(request, form, formsets, change)

        for formset in formsets:
            self.save_formset(request, form, formset, change=change)

    def get_fields(self, request, obj=None):
        if not obj:
            return 'name', 'template', 'profile'
        return super(DeckAdmin, self).get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'template', 'profile', 'cards_count', 'stat_learned_today_count', 'date_created', 'date_updated'
        return super(DeckAdmin, self).get_readonly_fields(request, obj)


class CardFrontContentInline(admin.StackedInline):
    model = CardFrontContent
    verbose_name = "Front of the card"
    exclude = ('template',)

    def get_min_num(self, request, obj=None, **kwargs):
        return 1

    def get_max_num(self, request, obj=None, **kwargs):
        return self.get_min_num(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


class CardBackContentInline(admin.StackedInline):
    model = CardBackContent
    verbose_name = "Back of the card"
    exclude = ('template',)

    def get_min_num(self, request, obj=None, **kwargs):
        return 1

    def get_max_num(self, request, obj=None, **kwargs):
        return self.get_min_num(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Card)
class CardAdmin(admin.ModelAdmin, DynamicArrayMixin):
    """
    Custom user's (profile's) deck's card admin page
    Allows full card edit (+ front and back)
    Shows some extra information
    """
    inlines = [CardFrontContentInline, CardBackContentInline, ]
    list_display = ('name', 'deck', 'profile', 'state')
    ordering = ('deck__profile',)
    filter_horizontal = ()

    class Media(DynamicArrayMixin.Media):
        css = {
            'all': DynamicArrayMixin.Media.css.get('all') + ('css/custom_admin.css',)
        }

    def profile(self, obj: Card):
        return obj.deck.profile

    profile.short_description = 'Profile'
    profile.admin_order_field = 'deck__profile'

    def get_fields(self, request, obj=None):
        if not obj:
            return 'name', 'deck'
        return super(CardAdmin, self).get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'template', 'deck', 'state', 'opened_date', 'next_date', 'profile', 'k'
        return super(CardAdmin, self).get_readonly_fields(request, obj)


admin.site.register(DeckTag)
