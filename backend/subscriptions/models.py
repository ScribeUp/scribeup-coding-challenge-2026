from django.db import models


class Transaction(models.Model):
    user_id = models.IntegerField(db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_name = models.CharField(max_length=255)
    charged_at = models.DateTimeField(db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-charged_at"]

    def __str__(self):
        return f"{self.merchant_name} ${self.amount} @ {self.charged_at:%Y-%m-%d}"
