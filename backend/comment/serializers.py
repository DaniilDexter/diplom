from rest_framework import serializers
from .models import Comment
from task.serializers import TaskSerializer
from authentication.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):

    task = TaskSerializer()
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = '__all__'