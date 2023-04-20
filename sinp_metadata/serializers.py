import logging

from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from sinp_nomenclatures.models import Nomenclature

from .models import AcquisitionFramework, ActorRole, Keyword, Organism

logger = logging.getLogger(__name__)


class NomenclatureLabel(serializers.ModelSerializer):
    class Meta:
        model = Nomenclature
        fields = ["code", "label"]


class SimpleOrganism(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ["id", "label"]


class SimpleUser(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ["id", "username"]


class Keywords(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ["keyword"]


class ActorRoleOrganism(serializers.ModelSerializer):
    name = SerializerMethodField()
    actor_type = SerializerMethodField()
    actor_role_label = SerializerMethodField()

    class Meta:
        model = ActorRole
        fields = [
            "name",
            "actor_type",
            "actor_role_label",
        ]

    def get_actor_role_label(self, ar):
        return ar.actor_role.label

    def get_actor_type(self, ar):
        if ar.organism:
            type = "Personne morale"
        elif ar.role:
            type = "Personne physique"
        else:
            type = None
        return type

    def get_name(self, ar):
        if ar.organism:
            name = ar.organism.label
        elif ar.role:
            name = ar.role.username
        else:
            name = None
        return name


class AcquisitionFrameworkSerializer(serializers.ModelSerializer):
    actor = ActorRoleOrganism(read_only=True, many=True)
    financing_type = NomenclatureLabel(read_only=True)
    objective = NomenclatureLabel(many=True, read_only=True)
    context = NomenclatureLabel(many=True, read_only=True)
    territory_level = NomenclatureLabel(read_only=True)
    territory = NomenclatureLabel(many=True, read_only=True)
    keywords = Keywords(many=True, read_only=True)

    class Meta:
        model = AcquisitionFramework
        fields = [
            "id_acquisition_framework",
            "uuid",
            "label",
            "desc",
            "context",
            "objective",
            "territory_level",
            "territory",
            "geo_accuracy",
            "keywords",
            "financing_type",
            "actor",
            "target_description",
            "is_metaframework",
            "parent_framework",
            "ecologic_or_geologic_target",
            "date_start",
            "date_end",
            "timestamp_create",
            "timestamp_update",
            "created_by",
        ]
        read_only_fields = [
            "timestamp_create",
            "timestamp_update",
            "uuid",
            "created_by",
        ]
        depth = 0


class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = [
            "id",
            "uuid",
            "label",
            "short_label",
            "action_scope",
            "geographic_area",
            "geographic_area_details",
            "status",
            "type",
            "address",
            "postal_code",
            "municipality",
            "email",
            "phone_number",
            "url",
            "created_by",
            "updated_by",
            "timestamp_create",
            "timestamp_update",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "timestamp_create",
            "timestamp_update",
            "uuid",
        ]
        depth = 0
