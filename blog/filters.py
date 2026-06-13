import django_filters
from django.db.models import Q
from .models import Post


class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    tag = django_filters.CharFilter(field_name='tags__slug')
    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(excerpt__icontains=value) |
            Q(body__icontains=value)
        ).distinct()

    class Meta:
        model = Post
        fields = ['category', 'tag', 'search']
