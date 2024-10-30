from django.db import models
from authentication.models import User, UserRole

class Project(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    owner = models.ForeignKey(User, verbose_name='Владелец', on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, verbose_name='Участники', through='ProjectMembers', related_name='projects')
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='изменён', auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

class ProjectMembers(models.Model):
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, verbose_name='Роль', on_delete=models.SET_NULL, null=True)
    joined_at = models.DateTimeField(verbose_name='Вступил',auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.role} в {self.project}"
    
    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проекта'