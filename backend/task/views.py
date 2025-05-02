from rest_framework.viewsets import ModelViewSet
from .models import Task, Subtask
from .serializers import TaskSerializer, SubtaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from column.models import Column
from report.models import Report
from comment.models import Comment
from django.db import transaction
from comment.serializers import CommentSerializer
from report.serializers import ReportSerializer
from django.utils import timezone  # Для текущего времени с учетом временной зоны
from datetime import timedelta, datetime  # Для работы с промежутками времени
from decimal import Decimal

class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Проверяем: был ли assigned_to пустым и пришёл в запросе
        was_unassigned = instance.assigned_to is None
        new_assignee = request.data.get('assigned_to') or request.data.get('assigned_to_id')

        self.perform_update(serializer)

        if was_unassigned and new_assignee:
            instance.assigned_at = timezone.now()
            instance.save(update_fields=["assigned_at"])

        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='add-task-to-column/(?P<column_id>[^/.]+)')
    def add_task_to_column(self, request, column_id=None):
        try:
            column = Column.objects.get(pk=column_id)
        except Column.DoesNotExist:
            return Response(
                {"error": "Column not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Определяем порядок для новой задачи
        last_order = Task.objects.filter(column=column).order_by('-order').first()
        new_order = (last_order.order + 1) if last_order else 0

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(column=column, order=new_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['PATCH'], url_path='update-column')
    def update_task_column(self, request, pk=None):
        task = self.get_object()
        new_column_id = request.data.get('column_id')
        new_order = request.data.get('order')  # <- тут

        if not new_column_id:
            return Response(
                {"error": "column_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_column = Column.objects.get(pk=new_column_id)
        except Column.DoesNotExist:
            return Response(
                {"error": "Column not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_order is None:
            last_order = Task.objects.filter(column=new_column).order_by('-order').first()
            new_order = (last_order.order + 1) if last_order else 0

        task.column = new_column
        task.order = new_order
        task.save()

        return Response(self.get_serializer(task).data)

    @action(detail=False, methods=['POST'], url_path='update-column-order/(?P<column_id>[^/.]+)')
    def update_column_order(self, request, column_id=None):
        try:
            column = Column.objects.get(pk=column_id)
        except Column.DoesNotExist:
            return Response(
                {"error": "Column not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        task_order = request.data.get('task_order', [])
        if not task_order:
            return Response(
                {"error": "task_order is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Обновляем порядок всех задач в колонке
                tasks = Task.objects.filter(id__in=task_order, column=column)
                task_dict = {str(task.id): task for task in tasks}
                
                for order, task_id in enumerate(task_order):
                    task = task_dict.get(str(task_id))
                    if task:
                        task.order = order
                        task.save(update_fields=['order'])
            
            return Response({"status": "order updated"})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['POST'], url_path='add-subtask')
    def add_subtask(self, request, pk=None):
        task = self.get_object()
        
        # Создаем копию данных и добавляем task_id
        data = request.data.copy()
        data['task'] = task.id  # Явно указываем ID задачи

        # Определяем порядок для новой подзадачи
        last_order = Subtask.objects.filter(task=task).order_by('-order').first()
        data['order'] = (last_order.order + 1) if last_order else 0

        # Создаем сериализатор с контекстом
        serializer = SubtaskSerializer(
            data=data,
            context={'task': task}  # Передаем задачу в контексте
        )
        
        if serializer.is_valid():
            # Сохраняем, явно указывая задачу
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['PATCH'], url_path='update-subtask')
    def update_subtask(self, request, pk=None):
        task = self.get_object()
        subtask_id = request.data.get('id')
        if not subtask_id:
            return Response({"error": "Subtask id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subtask = Subtask.objects.get(id=subtask_id, task=task)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubtaskSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'], url_path='delete-subtask')
    def delete_subtask(self, request, pk=None):
        task = self.get_object()
        subtask_id = request.data.get('id')
        if not subtask_id:
            return Response({"error": "Subtask id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subtask = Subtask.objects.get(id=subtask_id, task=task)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)

        subtask.delete()
        return Response({"status": "Subtask deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    
    @action(detail=True, methods=['POST'], url_path='add-comment')
    def add_comment(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Сохраняем комментарий с автором
            comment = serializer.save(task=task, author=request.user)

            # Если комментарий содержит одобрение, помечаем задачу как выполненную
            if getattr(comment, 'is_approved', False):  # если есть поле и оно True
                task.completed_at = timezone.now()
                task.is_completed = True
                task.save(update_fields=["completed_at", "is_completed"])

            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST', 'PUT'], url_path='update-report')
    def update_report(self, request, pk=None):
        task = self.get_object()
        data = request.data.copy()
        
        # Удаляем author_id из данных, если он есть
        data.pop('author_id', None)
        
        try:
            # Получаем или создаем отчет
            report, created = Report.objects.get_or_create(
                task=task,
                defaults={'author': request.user}  # Устанавливаем текущего пользователя
            )
            
            # Для файлов используем FormData
            form_data = {}
            for key, value in data.items():
                if key not in ['image', 'file']:
                    form_data[key] = value
            
            serializer = ReportSerializer(
                report, 
                data=form_data, 
                partial=not created,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                
                # Обработка файлов отдельно
                if 'image' in request.FILES:
                    report.image = request.FILES['image']
                if 'file' in request.FILES:
                    report.file = request.FILES['file']
                report.save()

                task.submitted_at = timezone.now()
                task.save(update_fields=["submitted_at"])
                
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=True, methods=['POST'], url_path='track-time')
    def track_time(self, request, pk=None):
        task = self.get_object()
        current_user = request.user

        try:
            if not task.is_timer_running:
                # ▶️ Запуск таймера
                task.timer_started_at = timezone.now()  # новое поле
                task.is_timer_running = True

                # Первый запуск вообще
                if not task.started_at:
                    task.started_at = timezone.now()
                    task.assigned_at = timezone.now()
                    task.assigned_to = current_user

                task.save()

                return Response({
                    'status': 'timer_started',
                    'started_at': task.started_at,
                    'total_time': task.time.strftime('%H:%M:%S') if task.time else '00:00:00'
                })

            else:
                # ⏸ Остановка таймера
                time_spent = timezone.now() - task.timer_started_at
                time_spent = timedelta(seconds=int(time_spent.total_seconds()))  # ⏱️ округляем до секунд

                # Суммируем с уже существующим временем (если оно есть)
                total_delta = timedelta()
                if task.time:
                    total_delta = timedelta(
                        hours=task.time.hour,
                        minutes=task.time.minute,
                        seconds=task.time.second
                    )

                total_delta += time_spent

                # Убираем микросекунды из окончательного времени
                total_time = (datetime.min + total_delta).replace(microsecond=0).time()

                task.time = total_time
                task.timer_started_at = None
                task.is_timer_running = False
                task.save()

                return Response({
                    'status': 'timer_stopped',
                    'time_spent': str(time_spent),
                    'total_time': total_time.strftime('%H:%M:%S')
                })

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
