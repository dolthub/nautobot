from __future__ import unicode_literals

from mptt.forms import TreeNodeChoiceField

from django import forms
from django.db.models import Count

from dcim.constants import VIFACE_FF_CHOICES
from dcim.formfields import MACAddressFormField
from dcim.models import Device, Interface, Platform, Rack, Region, Site
from extras.forms import CustomFieldBulkEditForm, CustomFieldForm, CustomFieldFilterForm
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    APISelect, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ChainedFieldsMixin,
    ChainedModelChoiceField, ChainedModelMultipleChoiceField, CommentField, ComponentForm, ConfirmationForm,
    ExpandableNameField, FilterChoiceField, SlugField, SmallTextarea,
)
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine


#
# Cluster types
#

class ClusterTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ['name', 'slug']


#
# Cluster groups
#

class ClusterGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ['name', 'slug']


#
# Clusters
#

class ClusterForm(BootstrapMixin, CustomFieldForm):

    class Meta:
        model = Cluster
        fields = ['name', 'type', 'group']


class ClusterCSVForm(forms.ModelForm):
    type = forms.ModelChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text='Name of cluster type',
        error_messages={
            'invalid_choice': 'Invalid cluster type name.',
        }
    )
    group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of cluster group',
        error_messages={
            'invalid_choice': 'Invalid cluster group name.',
        }
    )

    class Meta:
        model = Cluster
        fields = ['name', 'type', 'group']


class ClusterBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Cluster.objects.all(), widget=forms.MultipleHiddenInput)
    type = forms.ModelChoiceField(queryset=ClusterType.objects.all(), required=False)
    group = forms.ModelChoiceField(queryset=ClusterGroup.objects.all(), required=False)

    class Meta:
        nullable_fields = ['group']


class ClusterFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Cluster
    q = forms.CharField(required=False, label='Search')
    group = FilterChoiceField(
        queryset=ClusterGroup.objects.annotate(filter_count=Count('clusters')),
        to_field_name='slug',
        null_option=(0, 'None'),
        required=False,
    )
    type = FilterChoiceField(
        queryset=ClusterType.objects.annotate(filter_count=Count('clusters')),
        to_field_name='slug',
        required=False,
    )


class ClusterAddDevicesForm(BootstrapMixin, ChainedFieldsMixin, forms.Form):
    region = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'site', 'nullable': 'true'}
        )
    )
    site = ChainedModelChoiceField(
        queryset=Site.objects.all(),
        chains=(
            ('region', 'region'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/?region_id={{region}}',
            attrs={'filter-for': 'rack'}
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            attrs={'filter-for': 'devices', 'nullable': 'true'}
        )
    )
    devices = ChainedModelMultipleChoiceField(
        queryset=Device.objects.filter(cluster__isnull=True),
        chains=(
            ('site', 'site'),
            ('rack', 'rack'),
        ),
        label='Device',
        required=False,
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/?site_id={{site}}&rack_id={{rack}}',
            display_field='display_name',
            disabled_indicator='cluster'
        )
    )

    class Meta:
        fields = ['region', 'site', 'rack', 'devices']

    def __init__(self, *args, **kwargs):

        super(ClusterAddDevicesForm, self).__init__(*args, **kwargs)

        self.fields['devices'].choices = []


class ClusterRemoveDevicesForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)


#
# Virtual Machines
#

class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    cluster_group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'cluster', 'nullable': 'true'}
        )
    )
    cluster = ChainedModelChoiceField(
        queryset=Cluster.objects.all(),
        chains=(
            ('group', 'cluster_group'),
        ),
        widget=APISelect(
            api_url='/api/virtualization/clusters/?group_id={{cluster_group}}'
        )
    )

    class Meta:
        model = VirtualMachine
        fields = ['name', 'cluster_group', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments']

    def __init__(self, *args, **kwargs):

        # Initialize helper selector
        instance = kwargs.get('instance')
        if instance.pk and instance.cluster is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['cluster_group'] = instance.cluster.group
            kwargs['initial'] = initial

        super(VirtualMachineForm, self).__init__(*args, **kwargs)


class VirtualMachineCSVForm(forms.ModelForm):
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        help_text='Name of parent cluster',
        error_messages={
            'invalid_choice': 'Invalid cluster name.',
        }
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.'
        }
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned platform',
        error_messages={
            'invalid_choice': 'Invalid platform.',
        }
    )

    class Meta:
        model = VirtualMachine
        fields = ['name', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments']


class VirtualMachineBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), widget=forms.MultipleHiddenInput)
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all(), required=False)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    platform = forms.ModelChoiceField(queryset=Platform.objects.all(), required=False)
    vcpus = forms.IntegerField(required=False, label='vCPUs')
    memory = forms.IntegerField(required=False, label='Memory (MB)')
    disk = forms.IntegerField(required=False, label='Disk (GB)')
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['tenant', 'platform', 'vcpus', 'memory', 'disk']


class VirtualMachineFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VirtualMachine
    q = forms.CharField(required=False, label='Search')
    cluster_group = FilterChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        null_option=(0, 'None'),
    )
    cluster_id = FilterChoiceField(
        queryset=Cluster.objects.annotate(filter_count=Count('virtual_machines')),
        label='Cluster'
    )


#
# VM interfaces
#

class InterfaceForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = Interface
        fields = ['virtual_machine', 'name', 'form_factor', 'enabled', 'mac_address', 'mtu', 'description']
        widgets = {
            'virtual_machine': forms.HiddenInput(),
        }


class InterfaceCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(label='Name')
    form_factor = forms.ChoiceField(choices=VIFACE_FF_CHOICES)
    enabled = forms.BooleanField(required=False)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    mac_address = MACAddressFormField(required=False, label='MAC Address')
    description = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):

        # Set interfaces enabled by default
        kwargs['initial'] = kwargs.get('initial', {}).copy()
        kwargs['initial'].update({'enabled': True})

        super(InterfaceCreateForm, self).__init__(*args, **kwargs)


class InterfaceBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Interface.objects.all(), widget=forms.MultipleHiddenInput)
    virtual_machine = forms.ModelChoiceField(queryset=VirtualMachine.objects.all(), widget=forms.HiddenInput)
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['mtu', 'description']
