from rest_framework.viewsets import ModelViewSet

from .models import Priority
from .serializers import PrioritySerializer


class PriorityViewSet(ModelViewSet):
    serializer_class = PrioritySerializer
    queryset = Priority.objects.all()