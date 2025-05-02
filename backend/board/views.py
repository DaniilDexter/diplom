from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from .models import Board
from project.models import Project
from .serializers import BoardSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from column.models import Column
from column.serializers import ColumnSerializer


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.prefetch_related(
        'columns__tasks__subtasks',  # колонки → задачи → подзадачи
        'columns__tasks__tags',      # колонки → задачи → теги
        'columns__tasks__assigned_to' # колонки → задачи → исполнитель
    ).select_related('project')
    serializer_class = BoardSerializer
    queryset = Board.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Получаем query-параметры из запроса
        project_id = self.request.query_params.get('project')
        
        # Фильтруем queryset по project_id, если он передан
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

    def perform_create(self, serializer):
        project_id = self.request.data.get('project_id')
        if not project_id:
            raise serializers.ValidationError({"project": "This field is required."})
        
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError({"project": "Project not found."})
            
        serializer.save(project=project)

    @action(detail=True, methods=['POST'], url_path='add-column')
    def add_column(self, request, pk=None):
        board = self.get_object()
        serializer = ColumnSerializer(data=request.data, context={'board': board})  # Передаем board в контекст
        if serializer.is_valid():
            serializer.save()  # Не передаем board здесь, т.к. он уже в контексте
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)