from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.categories.models import Category


CATEGORIES = [
    "Maçon",
    "Plombier",
    "Électricien",
    "Menuisier",
    "Charpentier",
    "Couvreur",
    "Carreleur",
    "Peintre",
    "Plaquiste",
    "Façadier",
    "Serrurier",
    "Vitrier",
    "Soudeur",
    "Ferrailleur",
    "Étancheur",
    "Pisciniste",
    "Climatisation",
    "Frigoriste",
    "Chauffagiste",
    "Installateur solaire",
    "Électricien industriel",
    "Mécanicien automobile",
    "Électricien automobile",
    "Carrossier",
    "Peintre automobile",
    "Vulcanisateur",
    "Lavage automobile",
    "Ébéniste",
    "Fabricant de meubles",
    "Tapissier",
    "Couturier",
    "Styliste",
    "Coiffeur",
    "Coiffeuse",
    "Barbier",
    "Esthéticien",
    "Maquilleur",
    "Réparateur informatique",
    "Réparateur téléphone",
    "Réparateur télévision",
    "Réparateur électroménager",
    "Photographe",
    "Vidéaste",
    "Monteur vidéo",
    "Infographiste",
    "Jardinier",
    "Paysagiste",
    "Élagueur",
    "Agent de ménage",
    "Homme à tout faire",
    "Déménageur",
    "Foreur",
    "Puisatier",
    "Installateur fibre",
    "Antenniste",
    "Installateur vidéosurveillance",
    "Installateur d’alarmes",
    "Installateur de contrôle d’accès",
    "Décorateur",
    "Organisateur d’événements",
    "Traiteur",
    "Pâtissier",
    "Imprimeur",
    "Fabricant d’enseignes publicitaires",
    "Nettoyage industriel",
]


class Command(BaseCommand):
    help = "Ajoute les catégories initiales de métiers"

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for nom in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=slugify(nom),
                defaults={
                    "nom": nom,
                    "description": "",
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Créée : {category.nom}")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Existe déjà : {category.nom}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} catégories créées, "
                f"{existing_count} déjà existantes."
            )
        )
