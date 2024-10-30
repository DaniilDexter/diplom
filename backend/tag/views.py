from rest_framework.viewsets import ModelViewSet

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()