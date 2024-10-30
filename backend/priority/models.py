from django.db import models

class Priority(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Приоритет'
        verbose_name_plural = 'Приоритеты'
