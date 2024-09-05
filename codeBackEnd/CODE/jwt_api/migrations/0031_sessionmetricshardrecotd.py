# Generated by Django 5.0.6 on 2024-08-16 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0030_languages_session_session_language_ref"),
    ]

    operations = [
        migrations.CreateModel(
            name="sessionMetricsHardRecotd",
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