from django import forms
from django.utils.translation import gettext_lazy as _

from applications.models import Profile
from contents.models import DeckTemplate, Deck


class DeckTemplateCreationForm(forms.ModelForm):
    """
    A form for creating new deck template.
    Creates new or from existing decks
    """
    name = forms.CharField(max_length=128, required=False)
    creator = forms.ModelChoiceField(queryset=Profile.objects.get_queryset(), required=False)
    deck = forms.ModelChoiceField(
        label=_("From deck"),
        required=False,
        queryset=Deck.objects.get_queryset(),
        empty_label="(Nothing)",
        help_text="Or choose the deck that you want to create from",
    )

    class Meta:
        model = DeckTemplate
        fields = ('name', 'creator')

    def clean(self):
        if not self.cleaned_data.get("deck") and not self.cleaned_data.get("name"):
            raise forms.ValidationError({"name": _("This field is required if deck is not set")})

        if not self.cleaned_data.get("deck") and not self.cleaned_data.get("creator"):
            raise forms.ValidationError({"creator": _("This field is required if deck is not set")})

    def save(self, commit=True):
        if not self.cleaned_data.get("deck"):
            return super(DeckTemplateCreationForm, self).save(commit)
        return DeckTemplate.objects.create_from_deck(self.cleaned_data.get("deck"))
