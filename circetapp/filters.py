import django_filters
from .models import Parcours

class ParcoursFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(field_name='date_time', label='Intervalle de dates (YYYY-MM-DD)')

    class Meta:
        model = Parcours
        fields = ['date_range']