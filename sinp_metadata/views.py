import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import AcquisitionFramework, Organism
from .permissions import (
    AcquisitionFrameworkListPermissionsMixin,
    IsOrganismManager,
)
from .serializers import AcquisitionFrameworkSerializer, OrganismSerializer

logger = logging.getLogger(__name__)


class OrganismViewset(LoginRequiredMixin, ModelViewSet):
    serializer_class = OrganismSerializer
    permission_classes = [IsAuthenticated, IsOrganismManager]

    def get_queryset(self):
        logger.debug(f"ACTION: {self.action}")
        return Organism.objects.all()


class AcquisitionFrameworkViewset(
    LoginRequiredMixin,
    AcquisitionFrameworkListPermissionsMixin,
    ModelViewSet,
):
    serializer_class = AcquisitionFrameworkSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = AcquisitionFramework.objects.all()
