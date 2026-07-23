import django_filters

from .models import Artisan


class ArtisanFilter(django_filters.FilterSet):
    categorie = django_filters.CharFilter(
        field_name="categories__slug",
        lookup_expr="iexact",
    )

    categorie_id = django_filters.NumberFilter(
        field_name="categories__id",
    )

    ville = django_filters.CharFilter(
        field_name="ville",
        lookup_expr="iexact",
    )

    quartier = django_filters.CharFilter(
        field_name="quartier",
        lookup_expr="icontains",
    )

    verified = django_filters.BooleanFilter(
        field_name="verified",
    )

    experience_min = django_filters.NumberFilter(
        field_name="experience",
        lookup_expr="gte",
    )

    experience_max = django_filters.NumberFilter(
        field_name="experience",
        lookup_expr="lte",
    )

    class Meta:
        model = Artisan
        fields = (
            "categorie",
            "categorie_id",
            "ville",
            "quartier",
            "verified",
            "experience_min",
            "experience_max",
        )
