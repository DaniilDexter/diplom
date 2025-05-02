from django.db import models
from authentication.models import User
from task.models import Task

class Comment(models.Model):
    task = models.ForeignKey(Task, verbose_name='Задача', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Автор', related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Контент')
    is_approved = models.BooleanField(verbose_name='Одобрен?', default=False)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)

    def __str__(self):
        return f"Комментарий {self.author.username} к {self.task.title}"
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
