# Generated by Django 4.2.20 on 2025-04-09 22:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sinp_metadata", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="Unique ID (UUID)",
                    ),
                ),
                ("timestamp_create", models.DateTimeField(auto_now_add=True)),
                ("timestamp_update", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(unique=True, verbose_name="Label")),
                (
                    "description",
                    models.TextField(
                        blank=True, default="", verbose_name="Descriotion"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Active"),
                ),
            ],
            options={
                "verbose_name_plural": "projects",
            },
        ),
        migrations.AlterField(
            model_name="acquisitionframework",
            name="is_metaframework",
            field=models.BooleanField(
                default=False, verbose_name="Est un métacadre parent"
            ),
        ),
        migrations.AddConstraint(
            model_name="actorrole",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("legal_person__isnull", True),
                        ("organism__isnull", False),
                    ),
                    models.Q(
                        ("legal_person__isnull", False),
                        ("organism__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="sinp_metadata_actorrole_legal_person_or_organism",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="sinp_metadata.actorrole",
                verbose_name="Contact",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="dataset",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ds_project",
                to="sinp_metadata.project",
                verbose_name="Project",
            ),
        ),
    ]
