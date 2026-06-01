from django.http import JsonResponse

from .models import Transaction


def list_user_transactions(request, user_id: int):
    txns = Transaction.objects.filter(user_id=user_id).order_by("-charged_at")
    data = [
        {
            "id": t.id,
            "amount": str(t.amount),
            "merchant_name": t.merchant_name,
            "charged_at": t.charged_at.isoformat(),
            "raw_payload": t.raw_payload,
        }
        for t in txns
    ]
    return JsonResponse({"transactions": data})


def list_users(request):
    user_ids = (
        Transaction.objects.values_list("user_id", flat=True).distinct().order_by("user_id")
    )
    return JsonResponse({"user_ids": list(user_ids)})
