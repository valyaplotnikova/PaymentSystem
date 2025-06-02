import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import Payment, Organization


logger = logging.getLogger(__name__)


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["inn", "balance"]


class WebhookSerializer(serializers.ModelSerializer):
    payer_inn = serializers.CharField(write_only=True)

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

    def validate(self, data):
        if Payment.objects.filter(operation_id=data["operation_id"]).exists():
            logger.info(f"Платеж с operation_id {data['operation_id']} уже существует.")
            raise ValidationError({"detail": "Платеж уже существует"}, code="exists")
        return data

    def create(self, validated_data):
        inn = validated_data.pop("payer_inn")
        organization, created = Organization.objects.get_or_create(
            inn=inn, defaults={"balance": 0}
        )

        payment = Payment.objects.create(organization=organization, **validated_data)

        organization.balance += validated_data["amount"]
        organization.save(update_fields=["balance"])
        logger.info(
            f'Баланс организации {organization.inn} был изменен на {validated_data["amount"]} '
            f"и составил {organization.balance} рублей"
        )

        return payment
