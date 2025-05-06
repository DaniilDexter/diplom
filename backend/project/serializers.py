from rest_framework import serializers
from .models import Project, ProjectMembers
from board.models import Board
from tag.models import Tag
from priority.models import Priority

from board.serializers import BoardSerializer
from tag.serializers import TagSerializer
from priority.serializers import PrioritySerializer
from authentication.serializers import UserSerializer, UserRoleSerializer


class ProjectMembersSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = UserRoleSerializer()

    class Meta:
        model = ProjectMembers
        fields = ['user', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    boards = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    priorities = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'key', 'created_at', 'owner', 'boards', 'members', 'tags', 'priorities']

    def get_boards(self, obj):
        boards = Board.objects.filter(project=obj)
        return BoardSerializer(boards, many=True, context=self.context).data

    def get_tags(self, obj):
        tags = Tag.objects.filter(project=obj)
        return TagSerializer(tags, many=True).data

    def get_priorities(self, obj):
        priorities = Priority.objects.filter(project=obj)
        return PrioritySerializer(priorities, many=True).data

    def get_members(self, obj):
        members = ProjectMembers.objects.filter(project=obj).select_related('user', 'role')
        return ProjectMembersSerializer(members, many=True).data

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