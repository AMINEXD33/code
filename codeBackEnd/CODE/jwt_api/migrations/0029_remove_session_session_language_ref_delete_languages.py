# Generated by Django 5.0.6 on 2024-08-16 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0028_remove_languages_lang_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="session",
            name="session_language_ref",
        ),
        migrations.DeleteModel(
            name="languages",
        ),
    ]