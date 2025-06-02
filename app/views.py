import logging

from django.http import Http404
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Organization, Payment
from app.schemas import webhook_schema, balance_schema
from app.serializers import WebhookSerializer, OrganizationBalanceSerializer


logger = logging.getLogger(__name__)


@extend_schema_view(post=webhook_schema)
class WebhookView(APIView):
    def post(self, request):
        operation_id = request.data.get("operation_id")

        if not operation_id:
            return Response(
                {'"error": "operation_id обязателен"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Сначала проверяем наличие платежа
        if Payment.objects.filter(operation_id=operation_id).exists():
            return Response(
                {"status": "200 OK", "message": "Платёж уже был обработан ранее"},
                status=status.HTTP_200_OK,
            )

        # Только после этого запускаем сериалайзер
        serializer = WebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment = serializer.save()
        return Response(
            {
                "status": "success",
                "balance": str(payment.organization.balance),
                "operation_id": payment.operation_id,
            },
            status=status.HTTP_201_CREATED,
        )


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
