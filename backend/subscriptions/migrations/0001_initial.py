from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.IntegerField(db_index=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("merchant_name", models.CharField(max_length=255)),
                ("charged_at", models.DateTimeField(db_index=True)),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ["-charged_at"]},
        ),
    ]
