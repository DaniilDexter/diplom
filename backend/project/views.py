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
        queryset = Project.objects.filter(members=self.request.user)
        
        if self.action == 'list':
            queryset = queryset.order_by('-created_at')
        
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

        for user in users:
            role_id = 1 if user == request.user else user.role_id
            ProjectMembers.objects.filter(project=project, user=user).update(role_id=role_id)

        self.create_default_project_elements(project)


        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
    
    def create_default_project_elements(self, project):
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

        sprint_board = Board.objects.create(
            project=project,
            name='Спринт',
            is_sprint=True,
            icon='fxemoji:smallorangediamond'
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

    @action(detail=True, methods=['POST'], url_path='update-members')
    def update_members(self, request, pk=None):
        project = self.get_object()
        member_ids = request.data.get('members', [])

        if project.owner.id not in member_ids:
            member_ids.append(project.owner.id)

        users = User.objects.filter(id__in=member_ids)
        if users.count() != len(set(member_ids)):
            existing_ids = set(users.values_list('id', flat=True))
            invalid_ids = set(member_ids) - existing_ids
            return Response(
                {"detail": f"Не найдены пользователи с ID: {', '.join(map(str, invalid_ids))}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.members.set(users)

        for user in users:
            role_id = 1 if user == project.owner else user.role_id
            ProjectMembers.objects.update_or_create(
                project=project,
                user=user,
                defaults={'role_id': role_id}
            )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path='promote-to-leader')
    def promote_to_leader(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        ProjectMembers.objects.filter(project=project, user=user).update(role_id=1)
        
        project.refresh_from_db()
        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='demote-to-member')
    def demote_to_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_role_id = user.role_id
        
        ProjectMembers.objects.filter(project=project, user=user).update(role_id=user_role_id)
        
        project.refresh_from_db()
        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        project = self.get_object()

        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"detail": "Не указан ID пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_id == project.owner.id:
            return Response(
                {"detail": "Нельзя удалить владельца проекта"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        project.members.remove(user)
        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['GET'], url_path='boards')
    def get_project_boards(self, request, pk=None):

        project = Project.objects.get(pk=pk)
        
        boards = Board.objects.filter(project=project)
        serializer = BoardSerializer(boards, many=True, context={'request': request})
        
        return Response({
            'project_id': pk,
            'boards': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path='add-member-by-key')
    def add_member_by_key(self, request):
        key = request.data.get('key')  # Ключ проекта
        user_id = request.data.get('user_id')  # ID пользователя для добавления

        if not key or not user_id:
            return Response({"detail": "Ключ проекта и ID пользователя обязательны."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(key=key)
        except Project.DoesNotExist:
            return Response({"detail": "Проект с таким ключом не найден."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if project.members.filter(id=user_id).exists():
            return Response({"detail": "Пользователь уже является участником проекта."}, status=status.HTTP_400_BAD_REQUEST)

        project.members.add(user)

        role_id = user.role_id  # Получаем роль пользователя
        ProjectMembers.objects.update_or_create(
            project=project,
            user=user,
            defaults={'role_id': role_id}
        )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
    
class ProjectMembersViewSet(ModelViewSet):
    serializer_class = ProjectMembersSerializer
    queryset = ProjectMembers.objects.all()