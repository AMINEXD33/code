# Generated by Django 5.0.6 on 2024-06-26 17:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session_correction_pool",
            name="correction",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="session_correction_pool",
            name="note",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="session_user_pool",
            name="code_content",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="users_stats",
            name="session_user_pool_ref",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.session_user_pool",
            ),
        ),
    ]
