# Generated by Django 3.1.3 on 2021-01-28 05:00

from django.db import migrations, models
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0122_standardize_name_length'),
    ]

    operations = [
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
