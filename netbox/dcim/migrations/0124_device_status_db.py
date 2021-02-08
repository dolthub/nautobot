# Generated by Django 3.1.3 on 2021-01-10 00:28

from django.db import migrations
import django.db.models.deletion
import extras.models.statuses
import extras.management


def populate_status_choices(apps, schema_editor):
    """
    Explicitly run the `create_custom_statuses` signal since it is only ran at
    post-migrate.

    When it is ran again post-migrate will be a noop.
    """
    app_config = apps.get_app_config('extras')
    extras.management.create_custom_statuses(app_config)


def populate_device_status_db(apps, schema_editor):
    """
    Iterate existing Devices and populate `status_db` from `status` field.
    """
    Status = apps.get_model('extras.status')
    Device = apps.get_model('dcim.device')
    ContentType = apps.get_model('contenttypes.contenttype')

    content_type = ContentType.objects.get_for_model(Device)
    custom_statuses = Status.objects.filter(content_types=content_type)

    for device in Device.objects.all():
        device.status_db = custom_statuses.get(name=device.status)
        device.save()


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0057_status_field'),
        ('dcim', '0123_add_custom_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='status_db',
            field=extras.models.statuses.StatusField(null=True, on_delete=django.db.models.deletion.PROTECT, to='extras.status', related_name='devices'),
        ),
        migrations.RunPython(
            populate_status_choices,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_device_status_db,
            migrations.RunPython.noop,
            hints={'model_name': 'device'},
        ),
    ]