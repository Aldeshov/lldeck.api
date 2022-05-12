from django.db.models import QuerySet, Q
from django_filters import rest_framework as filters

from contents.models import DeckTemplate, DeckTag, Deck


class DeckTemplateFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    tag = filters.CharFilter(method='filter')
    q = filters.CharFilter(method='filter')

    class Meta:
        model = DeckTemplate
        fields = ('name', 'tag')

    @classmethod
    def filter(cls, queryset: QuerySet, name, value):
        if name == 'tag':
            tags = DeckTag.objects.filter(name__contains=value.lower())
            return queryset.filter(tags__in=tags)
        elif name == 'q':
            tags = DeckTag.objects.filter(name__contains=value.lower())
            return queryset.filter(Q(tags__in=tags) | Q(name__contains=value.lower()))


class DeckFilter(DeckTemplateFilter):
    favorite = filters.NumberFilter(method='favorite_filter')
    template = filters.NumberFilter(method='template_filter')

    class Meta(DeckTemplateFilter.Meta):
        model = Deck

    @classmethod
    def favorite_filter(cls, queryset: QuerySet, name, value):
        if name == 'favorite' and value and value > 0:
            return queryset.filter(favorite=True)
        elif name == 'favorite':
            return queryset.filter(favorite=False)

    @classmethod
    def template_filter(cls, queryset: QuerySet, name, value):
        if name == 'template' and value and value > 0:
            return queryset.filter(~Q(template=None))
        elif name == 'template':
            return queryset.filter(template=None)
