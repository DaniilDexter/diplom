from rest_framework import serializers
from .models import Board 
from column.serializers import ColumnSerializer

class BoardSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(write_only=True)
    columns = ColumnSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'project_id', 'name', 'created_at', 'icon', 'columns', 'is_sprint']
        extra_kwargs = {
            'project_id': {'required': True}
        }