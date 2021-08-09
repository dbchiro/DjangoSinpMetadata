from django.urls import path

from .views import AcquisitionFrameworkViewset, OrganismViewset

app_name = "metadata"

urlpatterns = [
    # API
    path(
        "api/v1/metadata/organisms/list",
        OrganismViewset.as_view({"get": "list"}),
        name="organism_list_api",
    ),
    path(
        "api/v1/metadata/organisms/<int:pk>",
        OrganismViewset.as_view({"get": "retrieve"}),
        name="organism_detail_api",
    ),
    path(
        "api/v1/metadata/acquisition_framework/list",
        AcquisitionFrameworkViewset.as_view({"get": "list"}),
        name="acquisition_framework_list_api",
    ),
    path(
        "api/v1/metadata/acquisition_framework/",
        AcquisitionFrameworkViewset.as_view({"post": "create"}),
        name="acquisition_framework_list_api",
    ),
    path(
        "api/v1/metadata/acquisition_framework/<int:pk>",
        AcquisitionFrameworkViewset.as_view({"get": "retrieve"}),
        name="acquisition_framework_detail_api",
    ),
    path(
        "api/v1/metadata/acquisition_framework/<int:pk>",
        AcquisitionFrameworkViewset.as_view({"put": "partial-update"}),
        name="acquisition_framework_list_api",
    ),
    path(
        "api/v1/metadata/acquisition_framework/<int:pk>",
        AcquisitionFrameworkViewset.as_view({"delete": "destroy"}),
        name="acquisition_framework_list_api",
    ),
    # Pages
]
