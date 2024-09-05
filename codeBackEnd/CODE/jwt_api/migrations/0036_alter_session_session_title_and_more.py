# Generated by Django 5.0.6 on 2024-08-16 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0035_sessionmetricshardrecord_sessionmetric_sessionref"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="session_title",
            field=models.CharField(max_length=300, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="sessionmetricshardrecord",
            name="sessionMetric_total_students",
            field=models.IntegerField(default=0),
        ),
    ]