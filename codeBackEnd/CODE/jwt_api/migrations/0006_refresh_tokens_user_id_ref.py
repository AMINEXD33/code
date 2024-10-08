# Generated by Django 5.0.6 on 2024-07-02 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0005_alter_refresh_tokens_first_requester_ip"),
    ]

    operations = [
        migrations.AddField(
            model_name="refresh_tokens",
            name="user_id_ref",
            field=models.ForeignKey(
                default="NULL",
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.users",
            ),
        ),
    ]
