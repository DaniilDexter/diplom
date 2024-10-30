from rest_framework.viewsets import ModelViewSet

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()