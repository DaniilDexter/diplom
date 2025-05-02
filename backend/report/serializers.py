from rest_framework import serializers
from .models import Report
from authentication.serializers import UserSerializer

class ReportSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'author', 'comment', 'image', 'file', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
        extra_kwargs = {
            'image': {'required': False},
            'file': {'required': False}
        }

    def create(self, validated_data):
        # Автоматически устанавливаем автора
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)