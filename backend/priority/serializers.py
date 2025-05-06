# priority/serializers.py
from rest_framework import serializers
from .models import Priority

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'project', 'name', 'color', 'is_default', 'order']