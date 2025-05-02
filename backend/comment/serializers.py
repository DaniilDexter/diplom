from rest_framework import serializers
from .models import Comment
from authentication.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Только для чтения
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'is_approved', 'created_at']
        read_only_fields = ['id', 'author', 'created_at', 'task']  # Эти поля нельзя менять через API

    def create(self, validated_data):
        # Автор берется из контекста запроса
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)