from rest_framework import serializers

from .models import Report
from task.serializers import TaskSerializer
from authentication.serializers import UserSerializer


class ReportSerializer(serializers.ModelSerializer):

    task = TaskSerializer()
    author = UserSerializer()

    class Meta:
        model = Report
        fields = '__all__'