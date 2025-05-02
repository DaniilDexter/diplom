from rest_framework import serializers
from .models import Column
from task.serializers import BaseTaskSerializer  # Импортируем базовый сериализатор

class ColumnSerializer(serializers.ModelSerializer):
    tasks = BaseTaskSerializer(many=True, read_only=True)  # Используем базовый
    
    class Meta:
        model = Column
        fields = ['id', 'name', 'order', 'tasks']
        read_only_fields = ['board']

    def validate_name(self, value):
        board = self.context.get('board')
        if board and Column.objects.filter(board=board, name=value).exists():
            raise serializers.ValidationError(
                "Колонка с таким названием уже существует в этой доске"
            )
        return value

    def create(self, validated_data):
        # Достаем board из контекста
        board = self.context['board']
        return Column.objects.create(board=board, **validated_data)