from rest_framework.viewsets import ModelViewSet

from .models import Project, ProjectMembers
from .serializers import ProjectMembersSerializer, ProjectSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

class ProjectMembersViewSet(ModelViewSet):
    serializer_class = ProjectMembersSerializer
    queryset = ProjectMembers.objects.all()