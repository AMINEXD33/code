# Generated by Django 5.0.6 on 2024-08-16 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0038_alter_session_session_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sessionmetricshardrecord",
            name="sessionMetric_SessionRef",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.session",
                unique=True,
            ),
        ),
    ]