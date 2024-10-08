# Generated by Django 5.0.6 on 2024-08-16 15:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0018_remove_session_session_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="session_language",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.languages",
            ),
            preserve_default=False,
        ),
    ]
