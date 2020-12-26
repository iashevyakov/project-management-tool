from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

PROJECT_SPRINT_STATUSES = (
    ('open', 'Not started'),
    ('in_progress', 'In progress'),
    ('delay', 'Delayed'),
    ('closed', 'Completed')
)


class Project(models.Model):
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    title = models.CharField("Title", max_length=100, null=False, blank=False)
    short_name = models.CharField("Short name", null=False, blank=False, max_length=20)
    date_start = models.DateField("Date start", null=False, blank=False)
    redline = models.DateField("To be completed", null=True, blank=False)
    date_end = models.DateField("Deadline", null=False, blank=False)
    status = models.CharField("Status", choices=PROJECT_SPRINT_STATUSES, max_length=20)
    employees = models.ManyToManyField("Employee", verbose_name='Employees', null=True, blank=True,
                                       related_name='employee_projects')

    created_at = models.DateTimeField("Creation date", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Last modified", auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_projects',
                                   verbose_name='Created by',
                                   on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Sprint(models.Model):
    class Meta:
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'

    project = models.ForeignKey(Project, related_name='project_sprints', null=False, blank=False,
                                on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=100)
    date_start = models.DateField("Date start", null=False, blank=False)
    redline = models.DateField("To be completed", null=True, blank=False)
    date_end = models.DateField("Deadline", null=False, blank=False)
    status = models.CharField("Status", choices=PROJECT_SPRINT_STATUSES, max_length=20)

    created_at = models.DateTimeField("Creation date", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Last modified", auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_sprints', verbose_name='Created by',
                                   on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"({self.project.short_name}) {self.title}"


class Task(models.Model):
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    STATUSES = (
        ('to-do', 'Not started'),
        ('in_progress', 'In progress'),
        ('postponed', 'Postponed'),
        ('done', 'Completed'),
        ('delay', 'Delayed'),
        ('late', 'Being late')
    )

    PRIORITIES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    project = models.ForeignKey(Project, related_name='project_tasks', null=True, blank=False, verbose_name='Project',
                                on_delete=models.CASCADE)
    sprint = models.ForeignKey(Sprint, related_name='sprint_tasks', null=True, blank=True, verbose_name='Sprint',
                               on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", max_length=2000, null=True, blank=True)
    accept_criterion = models.TextField("Acceptance Criterion", max_length=2000, null=True, blank=True)
    deadline = models.DateTimeField("Deadline", null=True, blank=False)
    redline = models.DateTimeField("To be completed", null=True, blank=False)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_assigned', verbose_name='Assigned',
                                 on_delete=models.SET_NULL, null=True, blank=False)
    state = models.CharField("Status", max_length=20, choices=STATUSES, default='to-do')
    priority = models.CharField("Priority", max_length=20, choices=PRIORITIES, default=PRIORITIES[0][0])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', verbose_name='Created by',
                                   on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField("Creation date", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Last modified", auto_now=True, editable=False)

    sub_tasks = models.ManyToManyField('Task', related_name='parent_task', verbose_name='Subtasks', blank=True)

    def __str__(self):
        return "[%s] %s" % (self.number, self.title)

    @property
    def number(self):
        return f"{self.project.short_name}-{self.id}"


ROLES = (
    ('pm', 'Project Manager'),
    ('dev', 'Developer'),
    ('qa', 'QA engineer'),
    ('analyst', 'Analyst'),
    ('area_dev', 'Dev Area Lead'),
    ('area_qa', 'QA Area Lead'),
    ('area_analyst', 'Analyst Area Lead'),
    ('lead_dev', 'Dev Lead'),
    ('lead_qa', 'QA Lead'),
    ('lead_analyst', 'Analyst Lead'),
)


class Dates(models.Model):
    name = models.CharField("Date name", max_length=50)
    date = models.DateField("Date", null=False, blank=False)

    def __str__(self):
        return f"{self.date.day}.{self.date.month} | {self.name}"


class Employee(AbstractUser):
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    name = models.CharField("Full name", max_length=50, blank=False, null=False)
    role = models.CharField("Role", max_length=20, choices=ROLES, default=ROLES[0][0], blank=False, null=False)
    chief = models.ForeignKey('Employee', on_delete=models.SET_NULL, related_name='subordinates', null=True, blank=True,
                              verbose_name='Chief')
    birthday = models.DateField("Birthday", null=True, blank=True)
    dates = models.ManyToManyField('Dates', null=True, blank=True, verbose_name='Important dates')

    def __str__(self):
        return self.name


class Item(models.Model):
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    item_description = models.CharField("Description", max_length=200)
    is_done = models.BooleanField("Done", default=False)

    def __str__(self):
        return ''
