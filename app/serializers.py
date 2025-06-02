import logging

from rest_framework import serializers, status
from rest_framework.response import Response

from app.models import Payment, Organization
from app.validators import validate_inn

logger = logging.getLogger(__name__)


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["inn", "balance"]


class WebhookSerializer(serializers.ModelSerializer):
    payer_inn = serializers.CharField(write_only=True, validators=[validate_inn])

    class Meta:
        model = Payment
        fields = [
            "operation_id",
            "amount",
            "payer_inn",
            "document_number",
            "document_date",
        ]
        extra_kwargs = {
            "document_number": {"required": True},
            "document_date": {"required": True},
        }

    def create(self, validated_data):
        inn = validated_data.pop("payer_inn")
        org, created = Organization.objects.get_or_create(
            inn=inn, defaults={"balance": 0}
        )

        payment = Payment.objects.create(organization=org, **validated_data)
        org.balance += validated_data["amount"]
        org.save(update_fields=["balance"])

        logger.info(
            f"Баланс организации {org.inn} увеличен на {validated_data['amount']}"
        )
        return payment
