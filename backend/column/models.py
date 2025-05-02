# column/models.py
from django.db import models
from board.models import Board

class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    order = models.IntegerField()
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Колонка'
        verbose_name_plural = 'Колонки'
        unique_together = [['board', 'name']]
        ordering = ['order']