# Generated by Django 3.1.7 on 2021-02-22 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0003_populate_default_status_records'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitrepository',
            name='username',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]