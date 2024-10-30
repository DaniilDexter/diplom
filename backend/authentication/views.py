from rest_framework.viewsets import ModelViewSet

from authentication.models import User, UserRole
from authentication.serializers import UserRoleSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class UserRoleViewSet(ModelViewSet):
    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()