from django.db.models import QuerySet
from django_filters import rest_framework as filters

from contents.models import DeckTemplate, DeckTag


class DeckTemplateFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    tag = filters.CharFilter(method='tag_filter')

    class Meta:
        model = DeckTemplate
        fields = ('name', 'tag')

    @classmethod
    def tag_filter(cls, queryset: QuerySet, name, value):
        if name == 'tag':
            tags = DeckTag.objects.filter(name__contains=value.lower())
            return queryset.filter(tags__in=tags)
