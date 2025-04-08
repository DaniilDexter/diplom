from django.db import models
from board.models import Board
from column.models import Column
from authentication.models import User, UserRole
from priority.models import Priority
from tag.models import Tag

class Task(models.Model):
    board = models.ForeignKey(Board, verbose_name='Доска', on_delete=models.CASCADE, related_name='tasks')
    column = models.ForeignKey(Column, verbose_name='Колонка', on_delete=models.SET_NULL, null=True, related_name='tasks')
    title = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    image = models.ImageField(verbose_name='Фото', upload_to='tasks/images/', blank=True, null=True)
    assigned_to = models.ForeignKey(User, verbose_name='Исполнитель', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    role = models.ForeignKey(UserRole, verbose_name='Роль', on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey(Priority, verbose_name='Приоритет', on_delete=models.SET_NULL, null=True, related_name='tasks')
    due_date = models.DateField(verbose_name='Срок сдачи', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Изменён', auto_now=True)
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='tasks')
    assigned_at = models.DateTimeField(verbose_name='Назначена', null=True, blank=True)
    started_at = models.DateTimeField(verbose_name='Приступил к работе', null=True, blank=True)
    submitted_at = models.DateTimeField(verbose_name='Отправлена на проверку', null=True, blank=True)
    completed_at = models.DateTimeField(verbose_name='Выполнена', null=True, blank=True)
    time = models.TimeField(verbose_name='Время', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

class Subtask(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100)
    task = models.ForeignKey('Task', verbose_name='Задача', on_delete=models.CASCADE, related_name='subtasks')