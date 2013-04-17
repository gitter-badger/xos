from plstackapi.core.models import Site
from plstackapi.core.models import *
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple


class ReadonlyTabularInline(admin.TabularInline):
    can_delete = False
    extra = 0
    editable_fields = []

    def get_readonly_fields(self, request, obj=None):
        fields = []
        for field in self.model._meta.get_all_field_names():
            if (not field == 'id'):
                if (field not in self.editable_fields):
                    fields.append(field)
        return fields

    def has_add_permission(self, request):
        return False

class SliverInline(admin.TabularInline):
    model = Sliver
    fields = ['ip', 'name', 'slice', 'flavor', 'image', 'key', 'node', 'deploymentNetwork']
    extra = 0

class SiteInline(admin.TabularInline):
    model = Site
    extra = 0

class NodeInline(admin.TabularInline):
    model = Node
    extra = 0

class PlanetStackBaseAdmin(admin.ModelAdmin):
    save_on_top = False

class DeploymentNetworkAdminForm(forms.ModelForm):
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=('Sites'), is_stacked=False
        )
    )
    class Meta:
        model = DeploymentNetwork

    def __init__(self, *args, **kwargs):
        super(DeploymentNetworkAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['sites'].initial = self.instance.sites.all()

    def save(self, commit=True):
        deploymentNetwork = super(DeploymentNetworkAdminForm, self).save(commit=False)

        if commit:
            deploymentNetwork.save()

        if deploymentNetwork.pk:
            deploymentNetwork.sites = self.cleaned_data['sites']
            self.save_m2m()

        return deploymentNetwork

class DeploymentNetworkAdmin(PlanetStackBaseAdmin):
    form = DeploymentNetworkAdminForm
    inlines = [NodeInline,]

class SiteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'site_url', 'enabled', 'is_public', 'login_base']}),
        ('Location', {'fields': ['latitude', 'longitude']}),
        ('Deployment Networks', {'fields': ['deployments']})
    ]
    list_display = ('name', 'login_base','site_url', 'enabled')
    filter_horizontal = ('deployments',)
    inlines = [NodeInline,]
    search_fields = ['name']

class UserForm(forms.ModelForm):
    class Meta:
        password = forms.CharField(widget=forms.PasswordInput)
        model = User
        widgets = {
            'password': forms.PasswordInput(),
        }

class UserAdmin(admin.ModelAdmin):
    form = UserForm
    fieldsets = [
        ('User', {'fields': ['firstname', 'lastname', 'email', 'password', 'phone', 'user_url', 'is_admin', 'site']})
    ]
    list_display = ['firstname', 'lastname', 'email', 'password', 'phone', 'user_url', 'is_admin', 'site']
    search_fields = ['email'] 

class KeyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Key', {'fields': ['name', 'key', 'type', 'blacklisted', 'user']})
    ]
    list_display = ['name', 'key', 'type', 'blacklisted', 'user']

class SliceAdmin(PlanetStackBaseAdmin):
    fields = ['name', 'site', 'instantiation', 'description', 'slice_url']
    list_display = ('name', 'site','slice_url', 'instantiation')
    inlines = [SliverInline]

class SubnetAdmin(admin.ModelAdmin):
    fields = ['cidr', 'ip_version', 'start', 'end', 'slice']

class ImageAdmin(admin.ModelAdmin):
    fields = ['image_id', 'name', 'disk_format', 'container_format']

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'deploymentNetwork')
    list_filter = ('deploymentNetwork',)

class RoleAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Role', {'fields': ['role_type']})
    ]
    list_display = ('role_type',)

class PlainTextWidget(forms.Widget):
    def render(self, _name, value, attrs):
        return mark_safe(value) if value is not None else ''

class SliverForm(forms.ModelForm):
    class Meta:
        ip = forms.CharField(widget=PlainTextWidget)
        model = Sliver
        widgets = {
            'ip': PlainTextWidget(),
        } 

class SliverAdmin(admin.ModelAdmin):
    form = SliverForm
    fieldsets = [
        ('Sliver', {'fields': ['ip', 'name', 'slice', 'flavor', 'image', 'key', 'node', 'deploymentNetwork']})
    ]
    list_display = ['ip', 'name', 'slice', 'flavor', 'image', 'key', 'node', 'deploymentNetwork']

admin.site.register(Site, SiteAdmin)
admin.site.register(SitePrivilege)
admin.site.register(Slice, SliceAdmin)
admin.site.register(SliceMembership)
admin.site.register(Subnet, SubnetAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Sliver, SliverAdmin)
admin.site.register(Flavor)
admin.site.register(Key, KeyAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(DeploymentNetwork, DeploymentNetworkAdmin)

