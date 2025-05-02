# tag/models.py (если у вас есть приложение tag)
from django.db import models
from project.models import ProjectBasedModel

class Tag(ProjectBasedModel):
    """Теги, специфичные для проекта"""
    color = models.CharField(max_length=7, default='#808080')  # HEX цвет
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        unique_together = [['project', 'name']]