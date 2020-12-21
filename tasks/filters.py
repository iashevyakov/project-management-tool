from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from tasks.lib import get_employee_subordinates
from tasks.models import Employee, Sprint


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
        print(projects)
        sprints = []
        for project in projects:
            sprints.extend(project.project_sprints.all())
        return [(s.id, str(s)) for s in sprints]
