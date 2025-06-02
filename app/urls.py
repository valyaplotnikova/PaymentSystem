from django.urls import path

from app.views import WebhookView, GetOrganizationBalanceView

urlpatterns = [
    path("webhook/bank/", WebhookView.as_view(), name="webhook"),
    path(
        "organizations/<str:inn>/balance/",
        GetOrganizationBalanceView.as_view(),
        name="organization_balance",
    ),
]
