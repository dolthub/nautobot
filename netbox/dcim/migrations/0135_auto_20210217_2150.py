# Generated by Django 3.1.3 on 2021-02-17 21:50

import dcim.fields
from django.db import migrations, models
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0134_powerfeed_status_change_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cablepath',
            name='path',
        ),
        migrations.AddField(
            model_name='cablepath',
            name='path',
            field=dcim.fields.JSONPathField(
                base_field=models.CharField(max_length=40)
            ),
        ),
        migrations.RemoveField(
            model_name='rackreservation',
            name='units',
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='units',
            field=utilities.fields.JSONArrayField(base_field=models.PositiveSmallIntegerField(), default=[]),
            preserve_default=False,
        ),
    ]