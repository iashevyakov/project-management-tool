import json

from django.http import HttpResponse
from tasks.lib import get_employee_subordinates, get_employee_tasks
from tasks.models import Project


def get_options(request):
    id = request.GET.get('id', '')
    if not id:
        result = [[], [], []]
    else:
        project = Project.objects.get(id=id)
        sprints = [(s.id, str(s)) for s in project.project_sprints.all()]
        employees = [(e.id, str(e)) for e in get_employee_subordinates(request.user, include_self=False) if
                     e in project.employees.all()]
        project_tasks = project.project_tasks.all()
        tasks = project_tasks.filter(
            id__in=[task.id for task in get_employee_tasks(request.user, include_self=False)])
        tasks = [(t.id, str(t)) for t in tasks]
        result = [sprints, employees, tasks]
    return HttpResponse(json.dumps(result), content_type="application/json")