# Generated by Django 3.1.3 on 2021-02-04 21:49

import dcim.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0123_auto_20210128_0500'),
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
    ]