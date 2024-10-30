from rest_framework import serializers

from .models import Project, ProjectMembers
from authentication.serializers import UserSerializer, UserRoleSerializer



class ProjectSerializer(serializers.ModelSerializer):

    owner = UserSerializer()
    members = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = '__all__'

class ProjectMembersSerializer(serializers.ModelSerializer):

    project = ProjectSerializer()
    user = UserSerializer()
    role = UserRoleSerializer()

    class Meta:
        model = ProjectMembers
        fields = '__all__'