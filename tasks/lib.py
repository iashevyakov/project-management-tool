from datetime import datetime

from tasks.models import Employee, Task, Project, Sprint


class PmPermissionMixin:
    def only_for_pm(self, request):
        if request.user.is_anonymous:
            return True
        return True if request.user.role == 'pm' else False


def get_employee_subordinates(employee, include_self=False):
    r = []
    if include_self:
        r.append(employee)
    for e in Employee.objects.filter(chief=employee):
        _r = get_employee_subordinates(e, include_self=True)
        if 0 < len(_r):
            r.extend(_r)
    return r


def get_employee_tasks(employee, include_self=True):
    r = []
    if include_self:
        r.extend(employee.tasks_assigned.all())
    for e in Employee.objects.filter(chief=employee):
        _r = get_employee_tasks(e)
        if 0 < len(_r):
            r.extend(_r)
    return r


def delay_tasks():
    Task.objects.filter(
        state__in=('to-do', 'in_progress', 'postponed'),
        redline__lte=datetime.now()
    ).update(state='delay')

    Task.objects.filter(
        state__in=('to-do', 'in_progress', 'postponed', 'delay'),
        deadline__lte=datetime.now()
    ).update(state='late')


def delay_projects():
    Project.objects.filter(
        status__in=('open', 'in_progress'),
        redline__lt=datetime.now()
    ).update(status='delay')

    Project.objects.filter(
        status__in=('open', 'in_progress', 'delay'),
        date_end__lt=datetime.now()
    ).update(status='late')


def delay_sprints():
    Sprint.objects.filter(
        status__in=('open', 'in_progress'),
        redline__lt=datetime.now()
    ).update(status='delay')

    Sprint.objects.filter(
        status__in=('open', 'in_progress', 'delay'),
        date_end__lt=datetime.now()
    ).update(status='late')
