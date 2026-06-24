import django_filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from users.models.user import User


class UserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserFilter(django_filters.FilterSet):
    search    = django_filters.CharFilter(method='filter_search')
    rol       = django_filters.ChoiceFilter(choices=User.Rol.choices)
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ['rol', 'is_active']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value)   |
            Q(apellido__icontains=value) |  # ✅ añadido
            Q(email__icontains=value)
        )