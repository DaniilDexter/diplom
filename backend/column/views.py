from rest_framework.viewsets import ModelViewSet

from .models import Column
from .serializers import ColumnSerializer


class ColumnViewSet(ModelViewSet):
    serializer_class = ColumnSerializer
    queryset = Column.objects.all()