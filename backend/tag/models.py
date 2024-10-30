from django.db import models

class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=50, unique=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
