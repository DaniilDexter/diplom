from rest_framework import serializers

from .models import Board 
from project.serializers import ProjectSerializer


class BoardSerializer(serializers.ModelSerializer):

    project = ProjectSerializer()

    class Meta:
        model = Board
        fields = '__all__'