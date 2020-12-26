from adminfilters.multiselect import UnionFieldListFilter
from django.contrib.admin import SimpleListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, ChoiceDropdownFilter

from tasks.lib import get_employee_subordinates, get_employee_tasks
from tasks.models import Employee, Sprint, ROLES, Task


class EmployeeFilter(RelatedDropdownFilter):

    def field_choices(self, field, request, model_admin):
        employees = [(e.id, str(e)) for e in get_employee_subordinates(request.user, include_self=True)]
        return employees


class ProjectFilter(RelatedDropdownFilter):
    def field_choices(self, field, request, model_admin):
        projects = request.user.employee_projects.all().union(request.user.created_projects.all())
        return [(p.id, str(p)) for p in projects]


class SprintFilter(RelatedDropdownFilter):
    def field_choices(self, field, request, model_admin):
        projects = request.user.employee_projects.all().union(request.user.created_projects.all())
        sprints = []
        for project in projects:
            sprints.extend(project.project_sprints.all())
        return [(s.id, str(s)) for s in sprints]


class RoleFilter(SimpleListFilter):
    title = 'Role'
    parameter_name = 'employee__role'
    dict_ = dict(ROLES)

    def lookups(self, request, model_admin):
        employees = get_employee_subordinates(request.user, include_self=True)
        roles = set([(e.role, self.dict_[e.role]) for e in employees])
        return list(roles)

    def queryset(self, request, queryset):
        if not self.value():
            return Task.objects.filter(id__in=[task.id for task in get_employee_tasks(request.user)])
        return Task.objects.filter(employee__role=self.value())
