from django.db import models
from project.models import Project

class Board(models.Model):
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(verbose_name='Название', max_length=100)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)

    def __str__(self):
        return f"{self.name} в {self.project.name}"
    
    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'
