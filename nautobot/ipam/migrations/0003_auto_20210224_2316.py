# Generated by Django 3.1.7 on 2021-02-24 23:16

import django.core.validators
from django.db import migrations, models
import nautobot.utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0002_initial_part_2'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='service',
        #     name='ports',
        # ),
        migrations.AddField(
            model_name='service',
            name='ports',
            field=nautobot.utilities.fields.JSONArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)])),
        ),
    ]
