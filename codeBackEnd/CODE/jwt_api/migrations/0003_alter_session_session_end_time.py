# Generated by Django 5.0.6 on 2024-06-26 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0002_alter_session_correction_pool_correction_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="session_end_time",
            field=models.DateTimeField(null=True),
        ),
    ]
