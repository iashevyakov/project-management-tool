from datetime import datetime, date

from adminfilters.multiselect import UnionFieldListFilter
from django.contrib import admin, auth
from django.core.mail import send_mail
from django.db import models
from django.forms import Textarea
from django import forms
from django.utils import timezone

from pm.settings import email, EMAIL_HOST_USER
from .filters import EmployeeFilter, ProjectFilter, SprintFilter, RoleFilter
from .forms import TaskForm, SprintForm, ProjectForm
from .lib import PmPermissionMixin, get_employee_tasks, get_employee_subordinates, delay_tasks, delay_sprints, \
    delay_projects
from .models import Task, Item, Employee, Project, Sprint, Dates
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0

    fields = ('item_description', 'is_done')

    def has_add_permission(self, request, obj=None):
        if obj and obj.employee == request.user:
            return False
        return True

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.employee == request.user:
            return ('item_description',)
        else:
            return super(ItemInline, self).get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.employee == request.user:
            return False
        return True


class ProjectAdmin(admin.ModelAdmin, PmPermissionMixin):
    list_display = ('title', 'created_at', 'date_start', 'status', 'redline', 'date_end', 'last_modified')
    list_display_links = ('title',)
    search_fields = ('title', 'status')

    list_filter = (
        'date_start',
        'date_end',
        'status'
    )

    form = ProjectForm

    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')

    fieldsets = (  # Edition form
        (None, {'fields': ('title', 'short_name', 'date_start', 'redline', 'date_end', 'status',
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
                    {'fields': ('title', 'short_name', 'date_start', 'redline', 'date_end', 'status',
                                'employees')}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        delay_projects()
        queryset = Project.objects.filter(created_by=request.user)
        return queryset

    def render_change_form(self, request, context, *args, **kwargs):
        if kwargs['obj']:
            if kwargs['obj'].redline and kwargs['obj'].status in ('open', 'in_progress') and kwargs[
                'obj'].redline <= date.today():
                kwargs['obj'].status = 'delay'
                kwargs['obj'].save()
            elif kwargs['obj'].status in ('open', 'in_progress', 'delay') and kwargs[
                'obj'].date_end <= date.today():
                kwargs['obj'].status = 'late'
                kwargs['obj'].save()
        return super(ProjectAdmin, self).render_change_form(request, context, *args, **kwargs)

    def has_module_permission(self, request):
        return self.only_for_pm(request)

    def has_add_permission(self, request):
        return self.only_for_pm(request)

    def has_change_permission(self, request, obj=None):
        return self.only_for_pm(request)

    def has_delete_permission(self, request, obj=None):
        return self.only_for_pm(request)


class SprintAdmin(admin.ModelAdmin, PmPermissionMixin):
    list_display = ('project', 'title', 'created_at', 'date_start', 'status', 'redline', 'date_end', 'last_modified')
    list_display_links = ('title',)
    search_fields = ('title', 'status')

    list_filter = (
        'date_start',
        'date_end',
        'status',
    )

    form = SprintForm

    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_modified', 'created_by')

    fieldsets = (  # Edition form
        (None, {'fields': ('project', 'title', 'date_start', 'redline', 'date_end',
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
                    {'fields': ('project', 'title', 'date_start', 'redline', 'date_end',
                                'status')}),
            )
        return fieldsets

    def render_change_form(self, request, context, *args, **kwargs):
        if kwargs['obj']:
            print(kwargs['obj'].redline)
            print(kwargs['obj'].date_end)
            print(date.today())
            if kwargs['obj'].redline and kwargs['obj'].status in ('open', 'in_progress') and kwargs[
                'obj'].redline <= date.today():
                kwargs['obj'].status = 'delay'
                kwargs['obj'].save()
            elif kwargs['obj'].status in ('open', 'in_progress', 'delay') and kwargs[
                'obj'].date_end <= date.today():
                kwargs['obj'].status = 'late'
                kwargs['obj'].save()
        context['adminform'].form.fields['project'].queryset = request.user.created_projects.all()
        return super(SprintAdmin, self).render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if change is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        delay_sprints()
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


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'number', 'title', 'project', 'sprint', 'employee', 'created_at', 'redline', 'deadline', 'priority', 'state')
    list_display_links = ('number', 'title')
    search_fields = ('id', 'title',
                     'employee__name', 'priority', 'state')
    list_filter = (
        RoleFilter,
        ('employee', EmployeeFilter),
        ('project', ProjectFilter),
        ('sprint', SprintFilter),
        ('state', UnionFieldListFilter),
        ('priority', UnionFieldListFilter),
        'deadline',
    )

    form = TaskForm
    filter_horizontal = ('sub_tasks',)

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
                        'project', 'sprint', 'title', 'description', 'state', 'priority', 'employee', 'redline',
                        'deadline',
                        'sub_tasks']}),
            )
        else:
            fieldsets = (  # Edition form
                (None,
                 {'fields': ['project', 'sprint', 'title', 'description', 'state', 'priority', 'employee', 'redline',
                             'deadline',
                             'sub_tasks']}),
                ("Доп.информация",
                 {'fields': (('created_at', 'last_modified'), 'created_by'), 'classes': ('collapse',)}),
            )

        if request.user.role in ('dev', 'qa', 'analyst'):
            fieldsets[0][1]['fields'].remove('deadline')

        return fieldsets

    def get_list_display(self, request):
        if request.user.role in ('dev', 'qa', 'analyst'):
            fields = list(self.list_display)
            fields.remove('deadline')
            return tuple(fields)
        else:
            return super(TaskAdmin, self).get_list_display(request)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # if obj.employee.email:
        #     if not change:
        #         send_mail(f"Назначена задача: {str(obj)}",
        #                   f'Назначена задача: {str(obj)} от {request.user.name}',
        #                   EMAIL_HOST_USER, [obj.employee.email])
        #     elif obj.employee != request.user:
        #         send_mail(f"Изменена задача: {str(obj)}",
        #                   f'Изменена задача: {str(obj)}',
        #                   EMAIL_HOST_USER, [obj.employee.email])

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.employee == request.user:
            print(self.readonly_fields)
            return tuple(self.readonly_fields) + (
                'project', 'sprint', 'title', 'description', 'employee', 'deadline', 'priority', 'redline')
        else:
            return super(TaskAdmin, self).get_readonly_fields(request, obj)

    def get_queryset(self, request):
        delay_tasks()
        task_ids = [task.id for task in get_employee_tasks(request.user)]
        return Task.objects.filter(id__in=task_ids)

    def render_change_form(self, request, context, *args, **kwargs):
        if not kwargs['obj'] in request.user.tasks_assigned.all():
            context['adminform'].form.fields['project'].queryset = request.user.employee_projects.all().union(
                request.user.created_projects.all())
            if kwargs['obj']:
                print(timezone.now())
                print(kwargs['obj'].redline)
                if kwargs['obj'].state in ('to-do', 'in_progress', 'postponed') and kwargs[
                    'obj'].redline <= timezone.now():
                    kwargs['obj'].state = 'delay'
                    kwargs['obj'].save()
                elif kwargs['obj'].state in ('to-do', 'in_progress', 'postponed', 'delay') and kwargs[
                    'obj'].deadline <= timezone.now():
                    kwargs['obj'].state = 'late'
                    kwargs['obj'].save()
                project_tasks = kwargs['obj'].project.project_tasks.all()
                tasks = project_tasks.filter(
                    id__in=[task.id for task in get_employee_tasks(request.user, include_self=False)])

                project_employees = kwargs['obj'].project.employees.all()
                employees = project_employees.filter(
                    id__in=[e.id for e in get_employee_subordinates(request.user, include_self=False)])

                context['adminform'].form.fields['sprint'].queryset = kwargs['obj'].project.project_sprints.all()
                context['adminform'].form.fields['employee'].queryset = employees
                context['adminform'].form.fields['sub_tasks'].queryset = tasks

            else:
                # pass
                context['adminform'].form.fields['employee'].queryset = Employee.objects.none()
                # context['adminform'].form.fields['sub_tasks'].queryset = Task.objects.none()
                context['adminform'].form.fields['sprint'].queryset = Sprint.objects.none()
        else:
            if kwargs['obj'].state in ('to-do', 'in_progress', 'postponed') and kwargs[
                'obj'].redline < datetime.now():
                kwargs['obj'].state = 'delay'
                kwargs['obj'].save()
            elif kwargs['obj'].state in ('to-do', 'in_progress', 'postponed', 'delay') and kwargs[
                'obj'].deadline < datetime.now():
                kwargs['obj'].state = 'late'
                kwargs['obj'].save()
            project_tasks = kwargs['obj'].project.project_tasks.all()
            tasks = project_tasks.filter(
                id__in=[task.id for task in get_employee_tasks(request.user, include_self=False)])
            context['adminform'].form.fields['sub_tasks'].queryset = tasks
        return super(TaskAdmin, self).render_change_form(request, context, *args, **kwargs)

    def has_add_permission(self, request):
        if get_employee_subordinates(request.user):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.employee == request.user:
            return True
        elif get_employee_subordinates(request.user):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.employee == request.user:
            return False
        return True


class EmployeeAdmin(admin.ModelAdmin, PmPermissionMixin):
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
