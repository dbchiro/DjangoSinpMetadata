from django.contrib.gis import admin

# Register your models here.
from .models import (
    AcquisitionFramework,
    ActorRole,
    Dataset,
    Keyword,
    Project,
    Publication,
)

# from guardian.admin import GuardedModelAdmin


class AcquisitionFrameworkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "label",
        "date_start",
        "date_end",
        "timestamp_update",
    )
    list_filter = ("label",)
    search_fields = (
        "uuid",
        "label",
    )


class DatasetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "label",
        "acquisition_framework",
        "active",
        "timestamp_update",
    )
    list_filter = ("label", "acquisition_framework", "active")
    search_fields = ("uuid", "label")


class NomenclatureAdmin(admin.ModelAdmin):
    list_display = ("id_nomenclature", "type", "code", "label", "active")
    list_filter = ("type", "active")


class ActorRoleAdmin(admin.ModelAdmin):
    list_display = (
        "legal_person",
        "organism",
        "actor_role",
        "anonymization",
        "timestamp_update",
    )
    list_filter = ("organism", "actor_role", "anonymization")
    search_fields = ("uuid", "legal_person", "organism")


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "label",
        "contact",
        "timestamp_update",
    )
    list_filter = ("contact",)
    search_fields = ("uuid", "label")


# Register your models here.
admin.site.register(Project, admin.ModelAdmin)
admin.site.register(AcquisitionFramework, AcquisitionFrameworkAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(ActorRole, ActorRoleAdmin)
admin.site.register(Publication)
admin.site.register(Keyword)
