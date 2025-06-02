from drf_spectacular.utils import OpenApiResponse, OpenApiExample, extend_schema

from app.serializers import WebhookSerializer, OrganizationBalanceSerializer

webhook_schema = extend_schema(
    summary="Создание платежного вебхука",
    description="""
    Эндпоинт для обработки уведомлений от платежных систем.
    Особенности:
    - Идемпотентность: повторные запросы с тем же operation_id не изменяют состояние
    - Валидация: проверка формата ИНН (10 или 12 цифр) и суммы платежа
    - Асинхронная обработка: тяжелые операции вынесены в Celery tasks
    """,
    request=WebhookSerializer,
    responses={
        201: OpenApiResponse(
            description="Платеж успешно создан", response=WebhookSerializer
        ),
        200: OpenApiResponse(
            description="Платеж уже был обработан ранее",
        ),
        400: OpenApiResponse(
            description="Некорректные данные",
        ),
        422: OpenApiResponse(description="Ошибка валидации данных"),
    },
    examples=[
        OpenApiExample(
            "Успешный платеж",
            value={
                "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
                "amount": 145000,
                "payer_inn": "1234567890",
                "document_number": "PAY-328",
                "document_date": "2024-04-27T21:00:00Z",
            },
            request_only=True,
            description="Пример входящего вебхука от платежного шлюза",
        ),
    ],
    tags=["Платежи"],
    deprecated=False,
    operation_id="process_payment_webhook",
)

balance_schema = extend_schema(
    summary="Получить баланс организации по ИНН",
    description="Возвращает текущий баланс организации по переданному ИНН из URL.",
    responses={
        200: OrganizationBalanceSerializer,
        404: OpenApiResponse(
            description="Организация не найдена",
        ),
    },
    examples=[
        OpenApiExample(
            name="Баланс организации",
            value={"inn": "1234567890", "balance": "145000.00"},
            response_only=True,
            description="Пример успешного ответа с балансом",
        ),
        OpenApiExample(
            name="Организация не найдена",
            value={"error": "Организация не найдена"},
            response_only=True,
            status_codes=["404"],
            description="Пример ответа, если организация не существует",
        ),
    ],
    tags=["Организации"],
    operation_id="get_organization_balance",
)
