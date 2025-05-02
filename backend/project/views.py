from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Project, ProjectMembers
from board.models import Board
from .serializers import ProjectMembersSerializer, ProjectSerializer, ProjectCreateSerializer
from board.serializers import BoardSerializer
from priority.models import Priority
from tag.models import Tag
from board.models import Board
from column.models import Column

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import random
import string
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.none()

    def get_queryset(self):
        # Базовый queryset - все проекты, где пользователь является участником
        queryset = Project.objects.filter(members=self.request.user)
        
        # Можно добавить дополнительные фильтры в зависимости от действия
        if self.action == 'list':
            # Для списка проектов можно добавить сортировку или другие фильтры
            queryset = queryset.order_by('-created_at')  # например, сортировка по дате создания
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create_project':
            return ProjectCreateSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['POST'], url_path='create-project')
    def create_project(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Project.objects.filter(key=key).exists():
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        project = Project.objects.create(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            owner=request.user,
            key=key
        )

        member_ids = serializer.validated_data.get('members', [])
        
        if request.user.id not in member_ids:
            member_ids.append(request.user.id)

        users = User.objects.filter(id__in=member_ids)
        if users.count() != len(set(member_ids)):
            existing_ids = set(users.values_list('id', flat=True))
            invalid_ids = set(member_ids) - existing_ids
            return Response(
                {"detail": f"Не найдены пользователи с ID: {', '.join(map(str, invalid_ids))}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.members.add(*users)

        self.create_default_project_elements(project)

        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED
        )
    
    def create_default_project_elements(self, project):
        """Создает базовые элементы для нового проекта"""
        # 1. Создаем базовые приоритеты
        default_priorities = [
            {'name': 'Низкий', 'color': '#4CAF50', 'order': 0},
            {'name': 'Средний', 'color': '#FFC107', 'order': 1},
            {'name': 'Высокий', 'color': '#FF9800', 'order': 2},
            {'name': 'Критический', 'color': '#F44336', 'order': 3},
        ]
        
        for priority in default_priorities:
            Priority.objects.create(
                project=project,
                name=priority['name'],
                color=priority['color'],
                order=priority['order'],
                is_default=True
            )

        # 2. Создаем базовые теги
        default_tags = [
            {'name': 'Фронтенд', 'color': '#2196F3'},
            {'name': 'Бэкенд', 'color': '#673AB7'},
            {'name': 'Тестирование', 'color': '#009688'},
            {'name': 'Дизайн', 'color': '#E91E63'},
        ]
        
        for tag in default_tags:
            Tag.objects.create(
                project=project,
                name=tag['name'],
                color=tag['color'],
                is_default=True
            )

        # 3. Создаем доску спринта с базовыми колонками
        sprint_board = Board.objects.create(
            project=project,
            name='Спринт',
            is_sprint=True
        )

        default_columns = [
            {'name': 'Новые', 'order': 0},
            {'name': 'В работе', 'order': 1},
            {'name': 'На проверке', 'order': 2},
            {'name': 'Выполнено', 'order': 3},
        ]
        
        for column in default_columns:
            Column.objects.create(
                board=sprint_board,
                name=column['name'],
                order=column['order'],
                is_default=True
            )

        # 4. Создаем общую доску (опционально)
        general_board = Board.objects.create(
            project=project,
            name='Общая доска'
        )

        for column in default_columns:
            Column.objects.create(
                board=general_board,
                name=column['name'],
                order=column['order'],
                is_default=True
            )
    
    @action(detail=True, methods=['GET'], url_path='boards')
    def get_project_boards(self, request, pk=None):
        """
        Получение всех досок определенного проекта
        URL: /api/v1/project/<id>/boards/
        """

        project = Project.objects.get(pk=pk)
        
        boards = Board.objects.filter(project=project)
        serializer = BoardSerializer(boards, many=True, context={'request': request})
        
        return Response({
            'project_id': pk,
            'boards': serializer.data
        }, status=status.HTTP_200_OK)
    
class ProjectMembersViewSet(ModelViewSet):
    serializer_class = ProjectMembersSerializer
    queryset = ProjectMembers.objects.all()