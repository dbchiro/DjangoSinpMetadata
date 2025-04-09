import logging

# from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import BasePermission
from sinp_nomenclatures.models import Nomenclature
from sinp_organisms.models import OrganismMember

from .models import ActorRole

logger = logging.getLogger(__name__)


class AcquisitionFrameworkListPermissionsMixin(object):
    """Mixin used for Sighting lists permissions"""

    def get_queryset(self, *args, **kwargs):
        """QuerySet mixin

        Returns:
            queryset
        """

        qs = super().get_queryset()
        user = self.request.user
        # user = get_user_model().objects.get(id=logged_user.id)

        if user.access_all_data or user.edit_all_data or user.is_superuser:
            return qs
        else:
            user_organisms = user.organism_member.all()
            actor_role = ActorRole.objects.filter(
                Q(organism__in=user_organisms) | Q(role=user)
            )
            qs = qs.filter(Q(actor__in=actor_role) | Q(created_by=user))
            return qs


class IsOrganismManager(BasePermission):
    message = "Organism access not allowed."

    def has_object_permission(self, request, view, obj):
        try:
            user = request.user
            # logger.debug(f"request.user {request.user}")
            # logger.debug(
            #     f"request.user.is_superuser {request.user.is_superuser}"
            # )
            # logger.debug(f"pk {obj.pk}")
            manager_nomenclature = Nomenclature.objects.filter(
                type__mnemonic="member_level", code="manager"
            )
            orgamember = OrganismMember.objects.filter(
                organism=obj, member=user, code=manager_nomenclature
            )
            logger.debug(
                f"orgamember.memberlevel.code {orgamember.member_level.code}"
            )

            perm = (
                orgamember.exists()
                or user == obj.created_by
                or user.is_superuser
            )
            logger.debug(f"perm {perm}")
            return perm
        except Exception as e:
            logger.debug(f"{e}")
            return False
