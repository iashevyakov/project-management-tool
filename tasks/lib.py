from datetime import datetime

from tasks.models import Employee, Task


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
        redline__lt=datetime.now()
    ).update(state='delay')

    Task.objects.filter(
        state__in=('to-do', 'in_progress', 'postponed', 'delay'),
        deadline__lt=datetime.now()
    ).update(state='late')

