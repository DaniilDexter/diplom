from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Project, ProjectMembers
from .serializers import ProjectMembersSerializer, ProjectSerializer, ProjectCreateSerializer

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
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create_project':
            return ProjectCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['POST'], url_path='create-project')
    def create_project(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Генерация ключа проекта
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Project.objects.filter(key=key).exists():
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Создание проекта
        project = Project.objects.create(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            owner=request.user,
            key=key
        )

        # Получаем список ID участников
        member_ids = serializer.validated_data.get('members', [])
        
        # Добавляем владельца, если его нет в списке
        if request.user.id not in member_ids:
            member_ids.append(request.user.id)

        # Получаем существующих пользователей
        users = User.objects.filter(id__in=member_ids)
        if users.count() != len(set(member_ids)):
            existing_ids = set(users.values_list('id', flat=True))
            invalid_ids = set(member_ids) - existing_ids
            return Response(
                {"detail": f"Не найдены пользователи с ID: {', '.join(map(str, invalid_ids))}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Добавляем участников
        project.members.add(*users)

        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED
        )
    
class ProjectMembersViewSet(ModelViewSet):
    serializer_class = ProjectMembersSerializer
    queryset = ProjectMembers.objects.all()