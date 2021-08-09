from django.contrib import admin

# Register your models here.
from .models import (
    AcquisitionFramework,
    ActorRole,
    Dataset,
    Keyword,
    Nomenclature,
    Publication,
)


class AcquisitionFrameworkAdmin(admin.ModelAdmin):
    list_display = (
        "id_acquisition_framework",
        "label",
        "date_start",
        "date_end",
        "timestamp_update",
    )
    list_filter = ("label",)


class DatasetAdmin(admin.ModelAdmin):
    list_display = (
        "id_dataset",
        "label",
        "acquisition_framework",
        "active",
        "timestamp_update",
    )
    list_filter = ("label", "acquisition_framework", "active")


class NomenclatureAdmin(admin.ModelAdmin):
    list_display = ("id_nomenclature", "type", "code", "label", "active")
    list_filter = ("type", "active")


class OrganismAdmin(admin.ModelAdmin):
    list_display = (
        "id_organism",
        "short_label",
        "status",
        "type",
        "action_scope",
    )
    list_filter = ("type",)


class OrganismMemberAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "organism",
        "member_level",
    )
    list_filter = ("organism", "member_level")


# Register your models here.
admin.site.register(Nomenclature, NomenclatureAdmin)
admin.site.register(AcquisitionFramework, AcquisitionFrameworkAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(ActorRole)
admin.site.register(Publication)
admin.site.register(Keyword)
