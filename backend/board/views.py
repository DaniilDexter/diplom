from rest_framework.viewsets import ModelViewSet

from .models import Board
from .serializers import BoardSerializer


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()