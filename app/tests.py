import uuid

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APITestCase

from app.models import Organization, Payment


class WebhookFunctionalityTests(APITestCase):
    def setUp(self):
        """
        Подготовка данных перед каждым тестом

        - Создаёт организацию с нулевым балансом
        - Задаёт URL для вебхука и получения баланса
        - Генерирует валидные данные для тестирования
        """
        self.inn = "0123456789"
        self.org = Organization.objects.create(inn=self.inn, balance=0)
        self.webhook_url = reverse("webhook")
        self.balance_url = reverse("organization_balance", kwargs={"inn": self.inn})
        self.valid_payload = {
            "operation_id": str(uuid.uuid4()),
            "amount": "145000.00",
            "payer_inn": self.inn,
            "document_number": "PAY-328",
            "document_date": timezone.now().isoformat(),
        }

    def test_valid_payment_creates_organization(self):
        """
        Проверяет, что валидный платёж создаёт запись о платеже и корректно обновляет баланс
        """
        response = self.client.post(
            self.webhook_url, data=self.valid_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Payment.objects.filter(
                operation_id=self.valid_payload["operation_id"]
            ).exists()
        )

        org = Organization.objects.get(inn=self.inn)
        self.assertEqual(org.balance, float(self.valid_payload["amount"]))

    def test_duplicate_operation_id_raises_error(self):
        """
        Проверяет, что платеж с таким же operation_id не обрабатывается повторно и возвращает 200_OK
        """
        response = self.client.post(
            self.webhook_url, data=self.valid_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Payment.objects.filter(
                operation_id=self.valid_payload["operation_id"]
            ).exists()
        )
        response = self.client.post(
            self.webhook_url, data=self.valid_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_inn_length_fails_validation(self):
        """
        Проверяет, что неверная длина ИНН приводит к ошибке валидации

        Проверяются ИНН из 5 символов — должно вернуть 400 Bad Request
        """
        invalid_payload = {
            "operation_id": str(uuid.uuid4()),
            "amount": "145000",
            "payer_inn": 12345,
            "document_number": "PAY-328",
            "document_date": timezone.now().isoformat(),
        }
        response = self.client.post(
            self.webhook_url, data=invalid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_balance(self):
        """
        Проверяет успешное получение баланса организации по ИНН

        После зачисления средств — организация должна вернуть актуальный баланс
        """
        self.client.post(self.webhook_url, data=self.valid_payload, format="json")
        response = self.client.get(self.balance_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inn"], self.inn)
        self.assertEqual(response.data["balance"], self.valid_payload["amount"])

    def test_get_balance_unknown_organization(self):
        """
        Проверяет, что несуществующий ИНН возвращает 404 Not Found
        """
        url = reverse("organization_balance", kwargs={"inn": 0000000000})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
