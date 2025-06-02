# 🏦 PaymentSystem

Система приёма платежей от банка и начисления средств организациям по ИНН.

## 🧾 Основные возможности

- Приём JSON-вебхуков
- Защита от дубликатов через `operation_id`
- Валидация ИНН (10 или 12 цифр)
- Обновление баланса организации
- Получение текущего баланса по ИНН
- Автоматическая документация через Swagger / drf-spectacular

---

## 📌 Эндпоинты

| Метод | URL | Описание |
|------|-----|----------|
| POST | `/api/webhook/bank/` | Принять платёж от банка |
| GET | `/api/organizations/<inn>/balance/` | Получить баланс организации |

---

## 🧾 Формат вебхука

```json
{
  "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
  "payer_inn": "1234567890",
  "amount": 145000,
  "document_number": "PAY-328",
  "document_date": "2024-04-27T21:00:00Z"
}
```

---

## 📊 Ответ на `/api/organizations/<inn>/balance/`

```json
{
  "inn": "1234567890",
  "balance": "145000.00"
}
```

---

## 🔧 Установка и запуск

```bash
git clone https://github.com/valyaplotnikova/PaymentSystem.git
cd PaymentSystem
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 📄 Документация

Открой:

```
http://localhost:8000/api/docs/
```

---

## 💡 Технологии

- Python 3.9  
- Django 4.2.17 + DRF  
- MySQL  
- drf-spectacular (Swagger)  
- Logging  

---
