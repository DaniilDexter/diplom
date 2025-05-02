# tag/serializers.py (если есть)
from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'project', 'name', 'description', 'color', 'is_default']