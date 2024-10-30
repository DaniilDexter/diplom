from django.db import models
from authentication.models import User
from task.models import Task

class Report(models.Model):
    task = models.OneToOneField(Task, verbose_name='Задача', related_name='report', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Автор', related_name='reports', on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='Комент',)
    image = models.ImageField(verbose_name='Изображение', upload_to='reports/images', blank=True, null=True)
    file = models.FileField(verbose_name='Файл', upload_to='reports/files', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)

    def __str__(self):
        return f"Репорт о {self.task.title} от {self.author.username}"
    
    class Meta:
        verbose_name = 'Репорт'
        verbose_name_plural = 'Репорты'
