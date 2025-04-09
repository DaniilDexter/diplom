from rest_framework import serializers

from .models import Project, ProjectMembers
from authentication.models import User
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

class ProjectCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'members']
        extra_kwargs = {
            'owner': {'read_only': True},
            'key': {'read_only': True}
        }