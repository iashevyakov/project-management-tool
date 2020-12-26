import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from tasks.lib import get_employee_subordinates
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
        tasks = [(t.id, str(t)) for t in project.project_tasks.all()]
        result = [sprints, employees, tasks]
    return HttpResponse(json.dumps(result), content_type="application/json")
