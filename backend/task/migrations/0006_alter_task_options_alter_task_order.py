# Generated by Django 5.1.2 on 2025-04-19 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_subtask_is_completed_subtask_order_task_is_completed_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['order'], 'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи'},
        ),
        migrations.AlterField(
            model_name='task',
            name='order',
            field=models.IntegerField(default=0, verbose_name='Порядковый номер'),
        ),
    ]
