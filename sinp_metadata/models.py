from datetime import date
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gismodels
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from sinp_organisms.models import Organism

User = get_user_model()

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Les numéros de téléphones doivent être renseignés "
    "avec le format : '+999999999'. jusqu'à 15 chiffres sont autorisés",
)


# Create your models here.


class BaseModel(
    models.Model
):  # base class should subclass 'django.db.models.Model'
    timestamp_create = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_update = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class ActorRole(BaseModel):
    id_actor_role = models.AutoField(primary_key=True)
    role = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    organism = models.ForeignKey(
        Organism, blank=True, null=True, on_delete=models.SET_NULL
    )
    dataset = models.ForeignKey(
        "Dataset", blank=True, null=True, on_delete=models.SET_NULL
    )
    acquisition_framework = models.ForeignKey(
        "AcquisitionFramework",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    actor_role = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        on_delete=models.CASCADE,
        limit_choices_to={"type__mnemonic": "actor_role"},
        related_name="actor_role",
        verbose_name=_("Rôle de l'acteur"),
    )

    def __str__(self):
        if self.organism is not None:
            actor = self.organism
        else:
            actor = self.role

        return "{} ({})".format(actor.short_label, self.actor_role.label)

    class Meta:
        verbose_name_plural = _("rôles des acteurs")
        unique_together = (
            ("role", "dataset", "actor_role"),
            ("organism", "dataset", "actor_role"),
            ("role", "acquisition_framework", "actor_role"),
            ("organism", "acquisition_framework", "actor_role"),
        )


class Keyword(BaseModel):
    keyword = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name_plural = _("mots clés")


class Publication(BaseModel):
    id_publication = models.AutoField(primary_key=True)
    label = models.CharField(
        max_length=255, unique=True, verbose_name=_("Nom")
    )
    url = models.URLField(
        blank=True, null=True, verbose_name=_("URL de la publication")
    )
    reference = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Référence complète"),
        help_text=_("Suivant la nomenclature ISO 690"),
    )
    file = models.FileField(
        blank=True,
        null=True,
        upload_to="metadata/publications/",
        verbose_name=_("Fichier"),
    )

    def __str__(self):
        return "#{} {}".format(self.id_publication, self.label)

    class Meta:
        verbose_name_plural = _("publications")


class Dataset(BaseModel):
    id_dataset = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Identifiant unique"),
    )
    acquisition_framework = models.ForeignKey(
        "AcquisitionFramework",
        on_delete=models.CASCADE,
        verbose_name=_("Cadre d'acquisition"),
        related_name="ds_acquisition_framework",
    )
    label = models.CharField(
        max_length=150, unique=True, verbose_name=_("Nom du jeu de données")
    )
    short_label = models.CharField(
        max_length=30, unique=True, verbose_name=_("Libellé court")
    )
    desc = models.TextField(verbose_name=_("Description"))
    creation_date = models.DateField(
        default=now,
        verbose_name=_("Date de création"),
        help_text=_(
            "Date de création de la fiche de métadonnées du jeu de données."
        ),
    )
    revision_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date de révision"),
        help_text=_(
            "Date de révision du jeu de données ou de sa fiche de "
            "métadonnées. Il est fortement recommandé de remplir "
            "cet attribut si une révision de la fiche ou du jeu de "
            "données a été effectuée"
        ),
    )
    data_type = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"type__mnemonic": "data_type"},
        related_name="ds_data_type",
        verbose_name=_("Type de données"),
    )
    actor_role_user = models.ManyToManyField(
        User,
        through="ActorRole",
        through_fields=("dataset", "role"),
        verbose_name=_("Acteurs (personnes physiques)"),
        related_name="ds_actor_user",
    )
    actor_role_organism = models.ManyToManyField(
        Organism,
        through="ActorRole",
        through_fields=("dataset", "organism"),
        verbose_name=_("Acteurs (personnes morales)"),
        related_name="ds_actor_organism",
    )
    actor_sinp = models.ForeignKey(
        "ActorRole",
        related_name="ds_actor_sinp",
        verbose_name=_("Point de contact principal pour la plateforme SINP"),
        # TODO WIP on limit choices to acteur principal
        limit_choices_to={"actor_role__code": "1"},
        on_delete=models.DO_NOTHING,
    )
    keywords = models.ManyToManyField(
        "Keyword",
        blank=True,
        related_name="ds_keywords",
        verbose_name=_("Mots-clés"),
    )
    territory = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "territory"},
        related_name="ds_territory",
        verbose_name=_("Territoire"),
        help_text=_(
            "Cible géographique du jeu de données, "
            "ou zone géographique visée par le jeu"
        ),
    )
    marine_domain = models.BooleanField(
        default=False, verbose_name=_("Domaine maritime")
    )
    terrestrial_domain = models.BooleanField(
        default=True, verbose_name=_("Domaine terrestre")
    )
    # TODO Nomenclature Objectifs JDD et suivantes
    objective = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"type__mnemonic": "dataset_objective"},
        related_name="ds_objective",
        verbose_name=_("Objectifs"),
    )
    bbox = gismodels.PolygonField(
        srid=settings.GEODATA_SRID,
        null=True,
        blank=True,
        verbose_name=_("Emprise géographique"),
        help_text=_("rectangle permettant d'englober le jeu de données"),
    )
    collecting_method = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "collect_method"},
        related_name="ds_collecting_method",
        verbose_name=_("Méthode de recueil des données"),
        help_text=_(
            "Ensemble de techniques, savoir-faire et "
            "outils mobilisés pour collecter des données"
        ),
    )
    protocols = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "protocol_type"},
        related_name="ds_protocols",
        verbose_name=_("Protocoles"),
    )
    active = models.BooleanField(default=True, verbose_name=_("Actif"))
    validable = models.BooleanField(blank=True, verbose_name=_("Validable"))

    def __str__(self):
        return "#{} {}".format(self.id_dataset, self.label)

    class Meta:
        verbose_name_plural = _("jeux de données")


class AcquisitionFramework(BaseModel):
    id_acquisition_framework = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Identifiant unique"),
    )
    label = models.CharField(max_length=255, verbose_name=_("Libellé"))
    desc = models.TextField(verbose_name=_("Description"))
    context = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "context"},
        related_name="af_context",
        verbose_name=_("volet SINP"),
    )
    objective = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "objective"},
        related_name="af_objective",
        verbose_name=_("Objectifs"),
    )
    territory_level = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type__mnemonic": "territory_level"},
        related_name="af_territory_level",
        verbose_name=_("Niveau territorial"),
    )
    territory = models.ManyToManyField(
        "sinp_nomenclatures.Nomenclature",
        limit_choices_to={"type__mnemonic": "territory"},
        related_name="af_territory",
        verbose_name=_("Territoires"),
    )
    geo_accuracy = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type__mnemonic": "geo_accuracy"},
        related_name="af_geo_accuracy",
        verbose_name=_("Précision géographique"),
    )
    keywords = models.ManyToManyField(
        "Keyword",
        blank=True,
        related_name="af_keywords",
        verbose_name=_("Mots-clés"),
    )
    financing_type = models.ForeignKey(
        "sinp_nomenclatures.Nomenclature",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type__mnemonic": "financing_type"},
        related_name="af_financing_type",
        verbose_name=_("Type de financement"),
    )
    actor = models.ManyToManyField(
        "ActorRole", related_name="af_actor", verbose_name=_("Acteurs")
    )
    target_description = models.TextField(blank=True, null=True)
    is_metaframework = models.BooleanField(
        blank=True, null=True, verbose_name=_("Est un métacadre parent")
    )
    parent_framework = models.ForeignKey(
        "AcquisitionFramework",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"is_metaframework": True},
        related_name="metacadre",
        verbose_name=_("Métacadre parent"),
    )
    ecologic_or_geologic_target = models.TextField(blank=True, null=True)
    date_start = models.DateField(
        default=date.today, verbose_name=_("Date de début")
    )
    date_end = models.DateField(
        blank=True, null=True, verbose_name=_("Date de fin")
    )

    class Meta:
        verbose_name_plural = _("cadres d'acquisition")

    def __str__(self):
        return "#{} {}".format(self.id_acquisition_framework, self.label)

    def get_absolute_url(self):
        return reverse(
            "metadata:acquisition_framework_detail",
            kwargs={"pk": self.id_acquisition_framework},
        )


# @receiver(pre_save, sender=User)
# def pre_save_user(sender, instance, **kwargs):
#     if not instance._state.adding:
#         print("this is an update")
#     else:
#         print("this is an insert")

# method for updating
# @receiver(post_save, sender=User)
# def update_stock(sender, instance, **kwargs):
#     instance.product.stock -= instance.amount
#     instance.product.save()
