# Generated by Django 3.1.3 on 2021-02-04 17:47

import django.core.validators
from django.db import migrations, models
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0043_add_tenancy_to_aggregates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='ports',
        ),
        migrations.AddField(
            model_name='service',
            name='ports',
            field=utilities.fields.JSONArrayField(
                base_field=models.PositiveIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(65535)
                    ]
                )
            ),
            # preserve_default=False,
        ),
    ]