from rest_framework import serializers

from .models import Task
from board.serializers import BoardSerializer
from tag.serializers import TagSerializer
from column.serializers import ColumnSerializer
from priority.serializers import PrioritySerializer
from authentication.serializers import UserSerializer, UserRoleSerializer


class TaskSerializer(serializers.ModelSerializer):

    board = BoardSerializer()
    column = ColumnSerializer()
    assigned_to = UserSerializer()
    role = UserRoleSerializer()
    priority = PrioritySerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Task
        fields = '__all__'