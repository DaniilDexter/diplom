from django.db import models
from project.models import ProjectBasedModel

class Priority(ProjectBasedModel):
    """Приоритеты, специфичные для проекта"""
    color = models.CharField(max_length=7, default='#808080')  # HEX цвет
    order = models.IntegerField(default=0)  # Порядок отображения
    
    class Meta:
        verbose_name = 'Приоритет'
        verbose_name_plural = 'Приоритеты'
        unique_together = [['project', 'name']]
        ordering = ['order']