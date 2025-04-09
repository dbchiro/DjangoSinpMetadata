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
from sinp_nomenclatures.models import Nomenclature
from sinp_organisms.models import Organism

User = get_user_model()

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_(
        "Les numéros de téléphones doivent être renseignés "
        "avec le format : '+999999999'. jusqu'à 15 chiffres sont autorisés"
    ),
)


# Create your models here.


class BaseModel(
    models.Model
):  # base class should subclass 'django.db.models.Model'
    uuid = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Unique ID (UUID)"),
    )
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
    legal_person = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    organism = models.ForeignKey(
        Organism, blank=True, null=True, on_delete=models.CASCADE
    )
    actor_role = models.ForeignKey(
        Nomenclature,
        on_delete=models.CASCADE,
        limit_choices_to={"type__mnemonic": "roleActeur"},
        related_name="actor_role",
        verbose_name=_("Actor's role"),
    )
    anonymization = models.BooleanField(
        default=False,
        verbose_name=_("Anonymization"),
        help_text=_(
            "I want this actor's identity to be blurred "
            "when the data is distributed"
        ),
    )

    def __str__(self):
        actor = self.organism or self.legal_person
        return f"{actor} ({self.actor_role.label})"

    class Meta:
        verbose_name_plural = _("rôles des acteurs")
        unique_together = (
            ("legal_person", "actor_role"),
            ("organism", "actor_role"),
        )
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_legal_person_or_organism",
                check=(
                    models.Q(legal_person__isnull=True, organism__isnull=False)
                    | models.Q(
                        legal_person__isnull=False, organism__isnull=True
                    )
                ),
            )
        ]


class Keyword(BaseModel):
    keyword = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name_plural = _("key words")


class Publication(BaseModel):
    label = models.CharField(
        max_length=255, unique=True, verbose_name=_("Name")
    )
    url = models.URLField(
        blank=True, null=True, verbose_name=_("Publication URL")
    )
    reference = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Full reference"),
        help_text=_("According to ISO 690 nomenclature"),
    )
    file = models.FileField(
        blank=True,
        null=True,
        upload_to="metadata/publications/",
        verbose_name=_("File"),
    )

    def __str__(self):
        return f"#{self.pk} {self.label}"

    class Meta:
        verbose_name_plural = _("publications")


class OtherProtocolAndMethod(BaseModel):
    CATEGORY = (
        ("protocol", _("Protocol")),
        ("method", _("Method")),
    )

    category = models.CharField(choices=CATEGORY)
    label = models.CharField(verbose_name=_("Label"), unique=True)
    desc = models.TextField(verbose_name=_("Description"))
    reference = models.CharField(verbose_name=_("Reference"))

    def __str__(self):
        return f"#{self.pk} {self.label}"

    class Meta:
        verbose_name_plural = _("other protocols")


class SourceDatabase(BaseModel):
    label = models.CharField(verbose_name=_("Label"), unique=True)
    description = models.TextField(
        verbose_name=_("Description"), default="", blank=True
    )
    url = models.URLField(_("URL"), max_length=200)
    contact = models.ForeignKey(
        ActorRole,
        blank=True,
        null=True,
        verbose_name="Contact",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"#{self.pk} {self.label}"

    class Meta:
        verbose_name_plural = _("source databases")


class Project(BaseModel):
    label = models.CharField(verbose_name=_("Label"), unique=True)
    description = models.TextField(
        verbose_name=_("Descriotion"), default="", blank=True
    )
    contact = models.ForeignKey(
        ActorRole,
        verbose_name=_("Contact"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField(verbose_name=_("Active"), default=True)

    def __str__(self):
        return f"#{self.pk} {self.label}"

    class Meta:
        verbose_name_plural = _("projects")


class Dataset(BaseModel):
    acquisition_framework = models.ForeignKey(
        "AcquisitionFramework",
        on_delete=models.CASCADE,
        verbose_name=_("Acquisition framework"),
        related_name="ds_acquisition_framework",
    )
    project = models.ForeignKey(
        "Project",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("Project"),
        related_name="ds_project",
    )
    # linked_datasets = models.ManyToManyField(
    #     "self", verbose_name=_("Linked datasets")
    # )
    label = models.CharField(
        max_length=150, unique=True, verbose_name=_("Label")
    )
    short_label = models.CharField(
        max_length=30, unique=True, verbose_name=_("Short label")
    )
    desc = models.TextField(verbose_name=_("Description"))
    date_create = models.DateField(
        default=now,
        verbose_name=_("Create date"),
        help_text=_(
            "Date de création de la fiche de métadonnées du jeu de données."
        ),
    )
    data_type = models.ForeignKey(
        Nomenclature,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"type__mnemonic": "typeDonnees"},
        related_name="ds_data_type",
        verbose_name=_("Data type"),
    )
    data_category = models.ForeignKey(
        Nomenclature,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"type__mnemonic": "categorieDonnees"},
        related_name="ds_data_category",
        verbose_name=_("Data category"),
    )
    data_category_prec = models.TextField(
        default="", verbose_name=_("Précision sur la catégorie des données")
    )
    features = models.ManyToManyField(
        Nomenclature,
        blank=True,
        limit_choices_to={"type__mnemonic": "caracteristiqueJdd"},
        related_name="ds_features",
        verbose_name=_("Features"),
    )
    ebv_classes = models.ManyToManyField(
        Nomenclature,
        blank=True,
        limit_choices_to={"type__mnemonic": "classeEBV"},
        related_name="ds_ebv_classes",
        verbose_name=_("EBV classes (https://geobon.org/ebvs/what-are-ebvs/)"),
    )
    data_origin_status = models.ForeignKey(
        Nomenclature,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"type__mnemonic": "statutOrigineDonnees"},
        related_name="ds_data_origin_status",
        verbose_name=_("Data origin status"),
    )
    # TODO: Créer la nomenclature
    collecting_method = models.ManyToManyField(
        Nomenclature,
        limit_choices_to={"type__mnemonic": "CodeCAMPanule"},
        related_name="ds_collecting_method",
        verbose_name=_("Méthode de recueil des données"),
        help_text=_(
            "Ensemble de techniques, savoir-faire et "
            "outils mobilisés pour collecter des données"
        ),
    )
    method_precision = models.TextField(
        default="", verbose_name=_("Precisions on collecting method")
    )
    other_method = models.ForeignKey(
        OtherProtocolAndMethod,
        blank=True,
        null=True,
        limit_choices_to={"category": "method"},
        verbose_name=_("Other method"),
        related_name="ds_other_method",
        on_delete=models.SET_NULL,
    )
    collecting_protocol = models.ManyToManyField(
        Nomenclature,
        limit_choices_to={"type__mnemonic": "CodeCAMPanule"},
        related_name="ds_collecting_protocol",
        verbose_name=_("Protocole de recueil des données"),
        help_text=_(
            "Ensemble de techniques, savoir-faire et "
            "outils mobilisés pour collecter des données"
        ),
    )
    protocol_precision = models.TextField(
        default="", verbose_name=_("Precisions on collecting protocol")
    )
    other_protocol = models.ForeignKey(
        OtherProtocolAndMethod,
        blank=True,
        null=True,
        limit_choices_to={"category": "protocol"},
        verbose_name=_("Other protocol"),
        related_name="ds_other_protocol",
        on_delete=models.SET_NULL,
    )
    keywords = models.ManyToManyField(
        "Keyword",
        blank=True,
        related_name="ds_keywords",
        verbose_name=_("Mots-clés"),
    )
    territory = models.ManyToManyField(
        Nomenclature,
        limit_choices_to={"type__mnemonic": "territory"},
        related_name="ds_territory",
        verbose_name=_("Territoire"),
        help_text=_(
            "Cible géographique du jeu de données, "
            "ou zone géographique visée par le jeu"
        ),
    )
    bbox = gismodels.PolygonField(
        srid=settings.GEODATA_SRID,
        null=True,
        blank=True,
        verbose_name=_("Emprise géographique"),
        help_text=_("rectangle permettant d'englober le jeu de données"),
    )
    active = models.BooleanField(default=True, verbose_name=_("Actif"))
    validable = models.BooleanField(blank=True, verbose_name=_("Validable"))

    def __str__(self):
        return f"#{self.pk} {self.label}"

    class Meta:
        verbose_name_plural = _("jeux de données")
        permissions = (
            (
                "can_edit_self_dataset_organism",
                "Can edit dataset from user organism",
            ),
        )


class AcquisitionFramework(BaseModel):
    label = models.CharField(max_length=255, verbose_name=_("Libellé"))
    desc = models.TextField(verbose_name=_("Description"))
    objective = models.ManyToManyField(
        Nomenclature,
        limit_choices_to={"type__mnemonic": "objectifCA"},
        related_name="af_objective",
        verbose_name=_("Objectifs"),
    )
    territory_level = models.ForeignKey(
        Nomenclature,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type__mnemonic": "echelleTerritoriale"},
        related_name="af_territory_level",
        verbose_name=_("Niveau territorial"),
    )
    territory = models.ManyToManyField(
        Nomenclature,
        limit_choices_to={"type__mnemonic": "territoire"},
        related_name="af_territory",
        verbose_name=_("Territoires"),
    )
    keywords = models.ManyToManyField(
        "Keyword",
        blank=True,
        related_name="af_keywords",
        verbose_name=_("Mots-clés"),
    )
    actors = models.ManyToManyField(
        "ActorRole", related_name="af_actor", verbose_name=_("Acteurs")
    )
    target_description = models.TextField(blank=True, null=True)
    is_metaframework = models.BooleanField(
        default=False, verbose_name=_("Est un métacadre parent")
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
    date_create = models.DateField(
        default=date.today, verbose_name=_("Date de création")
    )
    date_start = models.DateField(
        default=date.today, verbose_name=_("Date de début")
    )
    date_end = models.DateField(
        blank=True, null=True, verbose_name=_("Date de fin")
    )

    class Meta:
        verbose_name_plural = _("cadres d'acquisition")
        permissions = (
            (
                "can_edit_self_acquisitionframework_organism",
                "Can edit acquisition framework from user organism",
            ),
        )

    def __str__(self):
        return "#{} {}".format(self.pk, self.label)

    def get_absolute_url(self):
        return reverse(
            "metadata:acquisition_framework_detail",
            kwargs={"pk": self.pk},
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
