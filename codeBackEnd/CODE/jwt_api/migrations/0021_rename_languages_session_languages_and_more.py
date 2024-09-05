# Generated by Django 5.0.6 on 2024-08-16 15:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0020_remove_session_session_language"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Languages",
            new_name="session_languages",
        ),
        migrations.RenameField(
            model_name="session_languages",
            old_name="language_id",
            new_name="session_languages_id",
        ),
        migrations.RenameField(
            model_name="session_languages",
            old_name="language_name",
            new_name="session_languages_name",
        ),
        migrations.AddField(
            model_name="session",
            name="session_language",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.session_languages",
            ),
            preserve_default=False,
        ),
    ]