from django.db import models

class Column(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100, unique=True)
    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Колонка'
        verbose_name_plural = 'Колонки'
