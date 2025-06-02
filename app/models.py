from django.db import models

from app.validators import validate_inn


class Organization(models.Model):
    """Модель организации, хранящая информацию об ИНН и балансе.

    Attributes:
        inn (CharField): ИНН организации (10-12 символов)
        balance (DecimalField): Текущий баланс организации
        created_at (DateTimeField): Дата создания записи
    """

    inn = models.CharField(
        max_length=12,
        validators=[validate_inn],
        unique=True,
        verbose_name="ИНН организации",
        help_text="Введите ИНН длиной от 10 до 12 символов",
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Баланс организации",
        help_text="Текущий баланс в рублях",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Организация, ИНН: {self.inn}"


class Payment(models.Model):
    """Модель платежа, связанная с организацией через ИНН.

    Attributes:
        operation_id (UUIDField): Уникальный идентификатор операции
        amount (PositiveIntegerField): Сумма платежа
        organization (ForeignKey): Ссылка на организацию
        document_number (CharField): Номер платежного документа
        document_date (DateTimeField): Дата документа
        created_at (DateTimeField): Дата создания записи
    """

    operation_id = models.UUIDField(
        unique=True,
        verbose_name="Идентификатор операции",
        help_text="Уникальный UUID операции",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Сумма платежа",
        help_text="Сумма в рублях",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        verbose_name="Организация",
        related_name="payments",
        help_text="Организация-плательщик",
    )
    document_number = models.CharField(
        max_length=50,
        verbose_name="Номер документа",
        help_text="Номер платежного документа",
    )
    document_date = models.DateTimeField(
        verbose_name="Дата документа", help_text="Дата создания документа"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-document_date"]
        indexes = [
            models.Index(fields=["operation_id"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["document_date"]),
        ]

    def __str__(self):
        return f"Платеж {self.document_number} - {self.amount} руб."
