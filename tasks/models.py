from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

PROJECT_SPRINT_STATUSES = (
    ('open', 'Открыт'),
    ('in_progress', 'В работе'),
    ('delay', 'Идёт с задержкой'),
    ('closed', 'Завершён')
)


class Project(models.Model):
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    title = models.CharField("Название", max_length=100, null=False, blank=False)
    short_name = models.CharField("Аббревиатура", null=False, blank=False, max_length=20)
    date_start = models.DateField("Дата начала", null=False, blank=False)
    date_end = models.DateField("Дата завершения", null=False, blank=False)
    status = models.CharField("Статус", choices=PROJECT_SPRINT_STATUSES, max_length=20)
    employees = models.ManyToManyField("Employee", verbose_name='Сотрудники', null=True, blank=True,
                                       related_name='employee_projects')

    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Последнее изменение", auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_projects',
                                   verbose_name='Кем создан',
                                   on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Sprint(models.Model):
    class Meta:
        verbose_name = 'Спринт'
        verbose_name_plural = 'Спринты'

    project = models.ForeignKey(Project, related_name='project_sprints', null=False, blank=False,
                                on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=100)
    date_start = models.DateField("Дата начала", null=False, blank=False)
    date_end = models.DateField("Дата завершения", null=False, blank=False)
    status = models.CharField("Статус", choices=PROJECT_SPRINT_STATUSES, max_length=20)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Последнее изменение", auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_sprints', verbose_name='Кем создан',
                                   on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"({self.project.short_name}) {self.title}"


class Task(models.Model):
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    STATUSES = (
        ('to-do', 'Поставлена'),
        ('in_progress', 'В работе'),
        ('postponed', 'Отложена'),
        ('done', 'Завершена'),
        ('delay', 'Идёт с задержкой'),
        ('late', 'Опоздание')
    )

    PRIORITIES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    project = models.ForeignKey(Project, related_name='project_tasks', null=True, blank=False, verbose_name='Проект',
                                on_delete=models.CASCADE)
    sprint = models.ForeignKey(Sprint, related_name='sprint_tasks', null=True, blank=True, verbose_name='Спринт',
                               on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", max_length=2000, null=True, blank=True)
    accept_criterion = models.TextField("Критерий приёмки", max_length=2000, null=True, blank=True)
    deadline = models.DateTimeField("Дата завершения", null=True, blank=False)
    redline = models.DateTimeField("Запасная дата завершения", null=True, blank=False)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_assigned', verbose_name='Ответственный',
                                 on_delete=models.SET_NULL, null=True, blank=False)
    state = models.CharField("Статус", max_length=20, choices=STATUSES, default='to-do')
    priority = models.CharField("Приоритет", max_length=20, choices=PRIORITIES, default=PRIORITIES[0][0])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', verbose_name='Кем создана',
                                   on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)
    last_modified = models.DateTimeField("Последнее изменение", auto_now=True, editable=False)

    sub_tasks = models.ManyToManyField('Task', related_name='parent_task', verbose_name='Подзадачи', blank=True)

    def __str__(self):
        return "[%s] %s" % (self.number, self.title)

    @property
    def number(self):
        return f"{self.project.short_name}-{self.id}"

    # def save(self, *args, **kwargs):
    #     task_created = self.pk is None
    #     super().save(*args, **kwargs)
    #     if task_created:
    #         self.send_new_task_email()


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
    name = models.CharField("Название даты", max_length=50)
    date = models.DateField("Дата", null=False, blank=False)

    def __str__(self):
        return f"{self.date.day}.{self.date.month} | {self.name}"


class Employee(AbstractUser):
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    name = models.CharField("ФИО", max_length=50, blank=False, null=False)
    role = models.CharField("Роль", max_length=20, choices=ROLES, default=ROLES[0][0], blank=False, null=False)
    chief = models.ForeignKey('Employee', on_delete=models.SET_NULL, related_name='subordinates', null=True, blank=True,
                              verbose_name='Начальник')
    birthday = models.DateField("Дата рождения", null=True, blank=True)
    dates = models.ManyToManyField('Dates', null=True, blank=True, verbose_name='Важные даты')

    def __str__(self):
        return self.name


class Item(models.Model):
    class Meta:
        verbose_name = "Чек лист"
        verbose_name_plural = "Чек листы"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    item_description = models.CharField("Описание", max_length=200)
    is_done = models.BooleanField("Done", default=False)

    def __str__(self):
        return self.item_description
