# Generated by Django 5.0.6 on 2024-08-16 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0033_delete_sessionmetricshardrecord"),
    ]

    operations = [
        migrations.CreateModel(
            name="sessionMetricsHardRecord",
            fields=[
                (
                    "sessionMetric_id",
                    models.BigAutoField(primary_key=True, serialize=False),
                ),
                ("sessionMetric_total_students", models.IntegerField()),
                ("sessionMEtric_students_done", models.IntegerField(default=0)),
                ("sessionMetric_totallines", models.IntegerField(default=0)),
                ("sessionMetric_totalerrors", models.IntegerField(default=0)),
                ("sessionMetric_blockedstudents", models.IntegerField(default=0)),
                ("sessionMetric_avgCodeComplexity", models.IntegerField(default=0)),
                ("sessionMetric_totalwordswriten", models.IntegerField(default=0)),
            ],
        ),
    ]