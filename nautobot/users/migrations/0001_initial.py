# Generated by Django 3.1.3 on 2021-02-20 08:07

import uuid
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import nautobot.utilities.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminGroup",
            fields=[],
            options={
                "verbose_name": "Group",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name="AdminUser",
            fields=[],
            options={
                "verbose_name": "User",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("auth.user",),
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="UserConfig",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "data",
                    models.JSONField(
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="config",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Preferences",
                "verbose_name_plural": "User Preferences",
                "ordering": ["user"],
            },
        ),
        migrations.CreateModel(
            name="Token",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("expires", models.DateTimeField(blank=True, null=True)),
                (
                    "key",
                    models.CharField(
                        max_length=40,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(40)],
                    ),
                ),
                ("write_enabled", models.BooleanField(default=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ObjectPermission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("enabled", models.BooleanField(default=True)),
                (
                    "actions",
                    nautobot.utilities.fields.JSONArrayField(base_field=models.CharField(max_length=30)),
                ),
                (
                    "constraints",
                    models.JSONField(
                        blank=True,
                        null=True,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(blank=True, related_name="object_permissions", to="auth.Group"),
                ),
                (
                    "object_types",
                    models.ManyToManyField(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(
                                    _negated=True,
                                    app_label__in=[
                                        "admin",
                                        "auth",
                                        "contenttypes",
                                        "sessions",
                                        "taggit",
                                        "users",
                                    ],
                                ),
                                models.Q(
                                    ("app_label", "auth"),
                                    ("model__in", ["group", "user"]),
                                ),
                                models.Q(
                                    ("app_label", "users"),
                                    ("model__in", ["objectpermission", "token"]),
                                ),
                                _connector="OR",
                            )
                        ),
                        related_name="object_permissions",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="object_permissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "permission",
                "ordering": ["name"],
            },
        ),
    ]
