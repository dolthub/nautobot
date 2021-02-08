# Generated by Django 3.1.3 on 2021-01-19 22:27

from django.db import migrations, models
import django.db.models.deletion
import extras.utils
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0056_add_custom_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('color', utilities.fields.ColorField(default='9e9e9e', max_length=6)),
                ('content_types', models.ManyToManyField(limit_choices_to=extras.utils.FeatureQuery('statuses'), related_name='statuses', to='contenttypes.ContentType')),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'statuses',
            },
        ),
    ]