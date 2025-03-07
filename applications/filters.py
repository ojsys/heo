import django_filters
from .models import Application

class ApplicationFilter(django_filters.FilterSet):
    program_name = django_filters.CharFilter(
        field_name='program__name',
        lookup_expr='icontains',
        label='Program Name'
    )
    status = django_filters.ChoiceFilter(
        choices=Application.STATUS_CHOICES
    )
    submitted_after = django_filters.DateFilter(
        field_name='submitted_at',
        lookup_expr='gte',
        label='Submitted After'
    )
    submitted_before = django_filters.DateFilter(
        field_name='submitted_at',
        lookup_expr='lte',
        label='Submitted Before'
    )

    class Meta:
        model = Application
        fields = ['program_name', 'status', 'submitted_after', 'submitted_before']