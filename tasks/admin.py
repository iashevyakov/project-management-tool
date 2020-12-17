from adminfilters.multiselect import UnionFieldListFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from advanced_filters.models import AdvancedFilter
from django.contrib import admin, auth
from django.db import models
from django.forms import Textarea

from .lib import PmPermissionMixin
from .models import Task, Item, Employee, Project, Sprint, Dates
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0


class ProjectAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin, PmPermissionMixin):
    list_display = ('title', 'created_at', 'date_start', 'status', 'date_end', 'last_modified')
    list_display_links = ('title',)
    search_fields = ('title', 'status')

    list_filter = (
        'date_start',
        'date_end',
        'status'
    )

    advanced_filter_fields = (
        'title',
        'date_start',
        'date_end',
        'status'
    )

    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')

    fieldsets = (  # Edition form
        (None, {'fields': ('title', 'date_start', 'date_end', 'status',
                           'employees')}),
        ("Доп.информация", {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 32})
        }
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (  # Creation form
                (
                    None,
                    {'fields': ('title', 'date_start', 'date_end', 'status',
                                'employees')}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = Project.objects.filter(created_by=request.user)
        return queryset

    def has_module_permission(self, request):
        return self.only_for_pm(request)

    def has_add_permission(self, request):
        return self.only_for_pm(request)

    def has_change_permission(self, request, obj=None):
        return self.only_for_pm(request)

    def has_delete_permission(self, request, obj=None):
        return self.only_for_pm(request)


class SprintAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin, PmPermissionMixin):
    list_display = ('title', 'created_at', 'date_start', 'status', 'date_end', 'last_modified')
    list_display_links = ('title',)
    search_fields = ('title', 'status')

    list_filter = (
        'date_start',
        'date_end',
        'status'
    )

    advanced_filter_fields = (
        'title',
        'date_start',
        'date_end',
        'status'
    )

    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')

    fieldsets = (  # Edition form
        (None, {'fields': ('project', 'title', 'date_start', 'date_end',
                           'status')}),
        ("Доп.информация", {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
    )

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 32})
        }
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (  # Creation form
                (
                    None,
                    {'fields': ('project', 'title', 'date_start', 'date_end',
                                'status')}),
            )
        return fieldsets

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['project'].queryset = request.user.created_projects.all()
        return super(SprintAdmin, self).render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = Sprint.objects.filter(created_by=request.user)
        return queryset

    def has_module_permission(self, request):
        return self.only_for_pm(request)

    def has_add_permission(self, request):
        return self.only_for_pm(request)

    def has_change_permission(self, request, obj=None):
        return self.only_for_pm(request)

    def has_delete_permission(self, request, obj=None):
        return self.only_for_pm(request)


class TaskAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'sprint', 'employee', 'created_at', 'deadline', 'priority', 'state')
    list_display_links = ('number', 'title')
    search_fields = ('id', 'title',
                     'employee__name', 'priority', 'state')
    list_filter = (
        ('employee', RelatedDropdownFilter),
        ('project', RelatedDropdownFilter),
        ('sprint', RelatedDropdownFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
        'deadline'
    )
    advanced_filter_fields = (
        'employee__username',
        'state',
        'priority',
        'deadline',
        'created_at',
        'created_by',
        'title',
        'description',
    )
    ordering = ('-created_at',)
    readonly_fields = ['created_at', 'last_modified', 'created_by']

    inlines = [ItemInline]

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 32})
        }
    }

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            fieldsets = (  # Creation form
                (
                    None,
                    {'fields': [
                        'project', 'sprint', 'title', 'description', 'state', 'priority', 'employee', 'deadline',
                        'redline',
                        'sub_tasks']}),
            )
        else:
            fieldsets = (  # Edition form
                (None,
                 {'fields': ['project', 'sprint', 'title', 'description', 'state', 'priority', 'employee', 'deadline',
                             'redline',
                             'sub_tasks']}),
                ("Доп.информация",
                 {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
            )

        if request.user.role in ('dev', 'qa', 'analyst'):
            fieldsets[0][1]['fields'].remove('redline')
        return fieldsets

    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['project'].queryset = request.user.employee_projects.all()
    #     return super(TaskAdmin, self).render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.employee == request.user:
            return tuple(self.readonly_fields) + (
                'project', 'sprint', 'title', 'description', 'employee', 'deadline', 'priority', 'redline')
        else:
            return super(TaskAdmin, self).get_readonly_fields(request, obj)

    # def get_queryset(self, request):
    #     tasks = get_employee_tasks(request.user)
    #     return Task.objects.filter(id__in=[t.id for t in tasks])

    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['employee'].queryset = get_employee_subordinates(request.user)
    #     return super(TaskAdmin, self).render_change_form(request, context, *args, **kwargs)

    # def has_add_permission(self, request):
    #     if get_employee_subordinates(request.user):
    #         print(len(get_employee_subordinates(request.user)))
    #         return True
    #     return False
    # # #
    # # def has_change_permission(self, request, obj=None):
    # #     if get_employee_subordinates(request.user):
    # #         return True
    # #     return False


class EmployeeAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin, PmPermissionMixin):
    list_display = ('name', 'role', 'email')
    search_fields = ('username', 'name', 'role', 'email')

    ordering = ('name',)

    fieldsets = (  # Edition form
        (None, {'fields': ('username', 'email', 'name', 'role', 'chief', 'birthday', 'dates')}),
    )

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 4, 'cols': 32})
        }
    }

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.is_superuser = True
            obj.is_staff = True
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            fieldsets = (  # Creation form
                (
                    None,
                    {'fields': ('username', 'email', 'password', 'name', 'role', 'chief', 'birthday', 'dates')}),
            )
        return fieldsets

    def render_change_form(self, request, context, *args, **kwargs):
        if kwargs['obj']:
            context['adminform'].form.fields['dates'].queryset = kwargs['obj'].dates.all()
        else:
            context['adminform'].form.fields['dates'].queryset = Dates.objects.none()
        return super(EmployeeAdmin, self).render_change_form(request, context, *args, **kwargs)

    def has_module_permission(self, request):
        return self.only_for_pm(request)

    def has_add_permission(self, request):
        return self.only_for_pm(request)

    def has_change_permission(self, request, obj=None):
        return self.only_for_pm(request)

    def has_delete_permission(self, request, obj=None):
        return self.only_for_pm(request)


class DatesAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


admin.site.register(Project, ProjectAdmin)
admin.site.register(Sprint, SprintAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Dates, DatesAdmin)
admin.site.unregister(auth.models.Group)
admin.site.unregister(AdvancedFilter)
