import django_filters

from .models import DemandeTravaux


class DemandeTravauxFilter(django_filters.FilterSet):
    categorie = django_filters.CharFilter(
        field_name="categorie__slug",
        lookup_expr="iexact",
    )

    categorie_id = django_filters.NumberFilter(
        field_name="categorie__id",
    )

    ville = django_filters.CharFilter(
        field_name="ville",
        lookup_expr="iexact",
    )

    quartier = django_filters.CharFilter(
        field_name="quartier",
        lookup_expr="icontains",
    )

    statut = django_filters.ChoiceFilter(
        choices=DemandeTravaux.Statut.choices,
    )

    is_urgent = django_filters.BooleanFilter()

    budget_minimum = django_filters.NumberFilter(
        field_name="budget_max",
        lookup_expr="gte",
    )

    budget_maximum = django_filters.NumberFilter(
        field_name="budget_min",
        lookup_expr="lte",
    )

    class Meta:
        model = DemandeTravaux
        fields = (
            "categorie",
            "categorie_id",
            "ville",
            "quartier",
            "statut",
            "is_urgent",
            "budget_minimum",
            "budget_maximum",
        )
