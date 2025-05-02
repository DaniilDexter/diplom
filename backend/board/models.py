# board/models.py
from django.db import models
from project.models import Project

class Board(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(max_length=100)
    is_sprint = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'
        unique_together = [['project', 'name']]