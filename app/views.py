import logging

from django.http import Http404
from drf_spectacular.utils import extend_schema_view
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.parsers import JSONParser

from app.models import Organization
from app.schemas import webhook_schema, balance_schema
from app.serializers import WebhookSerializer, OrganizationBalanceSerializer


logger = logging.getLogger(__name__)


@extend_schema_view(post=webhook_schema)
class WebhookView(CreateAPIView):
    serializer_class = WebhookSerializer
    parser_classes = [JSONParser]


@extend_schema_view(get=balance_schema)
class GetOrganizationBalanceView(RetrieveAPIView):
    serializer_class = OrganizationBalanceSerializer
    lookup_field = "inn"
    queryset = Organization.objects.all()

    def get_object(self):
        inn = self.kwargs.get("inn")
        try:
            return self.queryset.get(inn=inn)
        except Organization.DoesNotExist:
            logger.info(f"Организация с ИНН {inn} не найдена")
            raise Http404("Организация не найдена")
