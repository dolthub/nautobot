import os
import random
import shutil
from datetime import timedelta

from cacheops.signals import cache_invalidated, cache_read
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_prometheus.models import model_deletes, model_inserts, model_updates
from prometheus_client import Counter

from .choices import ObjectChangeActionChoices
from .models import CustomField, GitRepository, ObjectChange
from .webhooks import enqueue_webhooks


#
# Change logging/webhooks
#

def _handle_changed_object(request, sender, instance, **kwargs):
    """
    Fires when an object is created or updated.
    """
    # Queue the object for processing once the request completes
    if kwargs.get('created'):
        action = ObjectChangeActionChoices.ACTION_CREATE
    elif 'created' in kwargs:
        action = ObjectChangeActionChoices.ACTION_UPDATE
    elif kwargs.get('action') in ['post_add', 'post_remove'] and kwargs['pk_set']:
        # m2m_changed with objects added or removed
        action = ObjectChangeActionChoices.ACTION_UPDATE
    else:
        return

    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(action)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Enqueue webhooks
    enqueue_webhooks(instance, request.user, request.id, action)

    # Increment metric counters
    if action == ObjectChangeActionChoices.ACTION_CREATE:
        model_inserts.labels(instance._meta.model_name).inc()
    elif action == ObjectChangeActionChoices.ACTION_UPDATE:
        model_updates.labels(instance._meta.model_name).inc()

    # Housekeeping: 0.1% chance of clearing out expired ObjectChanges
    if settings.CHANGELOG_RETENTION and random.randint(1, 1000) == 1:
        cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
        ObjectChange.objects.filter(time__lt=cutoff).delete()


def _handle_deleted_object(request, sender, instance, **kwargs):
    """
    Fires when an object is deleted.
    """
    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(ObjectChangeActionChoices.ACTION_DELETE)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Enqueue webhooks
    enqueue_webhooks(instance, request.user, request.id, ObjectChangeActionChoices.ACTION_DELETE)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


#
# Custom fields
#

def handle_cf_removed_obj_types(instance, action, pk_set, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is removed from one or more ContentTypes.
    """
    if action == 'post_remove':
        instance.remove_stale_data(ContentType.objects.filter(pk__in=pk_set))


def handle_cf_deleted(instance, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is deleted.
    """
    instance.remove_stale_data(instance.content_types.all())


m2m_changed.connect(handle_cf_removed_obj_types, sender=CustomField.content_types.through)
pre_delete.connect(handle_cf_deleted, sender=CustomField)


#
# Caching
#

cacheops_cache_hit = Counter('cacheops_cache_hit', 'Number of cache hits')
cacheops_cache_miss = Counter('cacheops_cache_miss', 'Number of cache misses')
cacheops_cache_invalidated = Counter('cacheops_cache_invalidated', 'Number of cache invalidations')


def cache_read_collector(sender, func, hit, **kwargs):
    if hit:
        cacheops_cache_hit.inc()
    else:
        cacheops_cache_miss.inc()


def cache_invalidated_collector(sender, obj_dict, **kwargs):
    cacheops_cache_invalidated.inc()


cache_read.connect(cache_read_collector)
cache_invalidated.connect(cache_invalidated_collector)


#
# Datasources
#

@receiver(pre_delete, sender=GitRepository)
def git_repository_pre_delete(instance, **kwargs):
    """
    When a GitRepository is deleted, remove it from the local filesystem.

    TODO: In a distributed NetBox deployment, each Django instance and/or RQ worker instance may have its own clone
    of this repository; we need some way to ensure that all such clones are deleted.
    For now we just delete the one that we have locally and rely on other methods (notably get_custom_jobs())
    to clean up other clones as they're encountered.
    """
    if os.path.isdir(instance.filesystem_path):
        shutil.rmtree(instance.filesystem_path)
