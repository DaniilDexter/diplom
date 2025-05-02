from rest_framework import serializers
from .models import Task, Subtask
from tag.serializers import TagSerializer
from priority.serializers import PrioritySerializer
from authentication.serializers import UserSerializer, UserRoleSerializer
from report.serializers import ReportSerializer
from comment.serializers import CommentSerializer

from authentication.models import User
from priority.models import Priority
from tag.models import Tag

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'is_completed', 'order']

class BaseTaskSerializer(serializers.ModelSerializer):
    # Для записи (input) — принимаем ID
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='assigned_to', 
        required=False, 
        allow_null=True,
        write_only=True  # не отображается в выводе
    )
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all(), 
        source='priority', 
        required=False, 
        allow_null=True,
        write_only=True
    )
    tags_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        source='tags', 
        many=True, 
        required=False,
        write_only=True
    )

    # Для чтения (output) — возвращаем полные объекты
    assigned_to = UserSerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True, read_only=True)
    report = ReportSerializer(read_only=True)  # отчет (OneToOne)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'image', 
            'assigned_to', 'assigned_to_id', 'role', 
            'priority', 'priority_id', 'due_date',
            'created_at', 'updated_at', 'tags', 'tags_ids', 'subtasks',
            'assigned_at', 'started_at', 'submitted_at',
            'completed_at', 'time', 'is_completed', 'order',
            'report', 'comments'
        ]

    def update(self, instance, validated_data):
        # Обрабатываем теги отдельно, так как они ManyToMany
        tags_data = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        
        if tags_data is not None:
            instance.tags.set(tags_data)
        
        return instance

class TaskSerializer(BaseTaskSerializer):
    column = serializers.SerializerMethodField()

    class Meta(BaseTaskSerializer.Meta):
        fields = BaseTaskSerializer.Meta.fields + ['column']

    def get_column(self, obj):
        from column.serializers import ColumnSerializer
        return ColumnSerializer(obj.column).data if obj.column else None