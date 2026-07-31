import django_filters
from django.db import models

class ListContentPageDisplayLabelFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        if kwargs.get('page'):
            self.page = kwargs.pop('page')
        super().__init__(*args, **kwargs)

    @property
    def field(self):
        from .models import ListContentPage
        qs = ListContentPage.objects.descendant_of(self.page).live().distinct()
        qs = qs.order_by('display_label').values_list('display_label', flat=True)
        self.extra["choices"] = [(o, o) for o in qs if bool(o)]
        return super().field

class PropertyFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        if kwargs.get('property'):
            self.property = kwargs.pop('property')
        if kwargs.get('page'):
            self.page = kwargs.pop('page')
        super().__init__(*args, **kwargs)

    @property
    def field(self):
        from .models import ListContentPage, ListContentPageProperties

        qs = (
            ListContentPageProperties.objects
            .select_related('page')
            .filter(name=self.property)
            .filter(page_id__in=models.Subquery(
                ListContentPage.objects
                .descendant_of(self.page)
                .live()
                .values('id')
            ))
            .distinct()
        )
        qs = qs.order_by('value').values_list('value', flat=True)
        self.extra["choices"] = [(o, o) for o in qs if bool(o)]
        return super().field

    def filter(self, qs, value):
        if not value:
            return qs
        
        prop_name = self.property
        qs = qs.filter(
            properties__name=prop_name,
            properties__value=value,
        )

        return qs.distinct() if self.distinct else qs
    