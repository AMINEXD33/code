# Generated by Django 5.0.6 on 2024-08-27 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0042_alter_sessionmetricshardrecord_sessionmetric_sessionref"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="session_user_pool",
            name="session_id_ref",
        ),
        migrations.RemoveField(
            model_name="session_user_pool",
            name="user_id_ref",
        ),
        migrations.RemoveField(
            model_name="users_stats",
            name="session_user_pool_ref",
        ),
        migrations.RemoveField(
            model_name="users_stats",
            name="user_id_ref",
        ),
        migrations.CreateModel(
            name="Session_user_tracking_record",
            fields=[
                (
                    "Session_user_tracking_record_id",
                    models.BigAutoField(primary_key=True, serialize=False),
                ),
                ("Session_user_tracking_record_code", models.TextField(default="")),
                ("Session_user_tracking_record_activity_starts_at", models.DateField()),
                ("Session_user_tracking_record_activity_ends_at", models.DateField()),
                ("Session_user_tracking_record_errors", models.JSONField()),
                ("Session_user_tracking_record_submitions", models.JSONField()),
                (
                    "Session_user_tracking_record_compilations",
                    models.IntegerField(default=0),
                ),
                (
                    "Session_user_tracking_record_lines_of_code",
                    models.IntegerField(default=0),
                ),
                ("Session_user_tracking_record_words", models.IntegerField(default=0)),
                (
                    "Session_user_tracking_record_summarized_lines_of_code",
                    models.JSONField(),
                ),
                ("Session_user_tracking_record_suspicious", models.JSONField()),
                (
                    "Session_user_tracking_record_code_complexity",
                    models.IntegerField(default=0),
                ),
                (
                    "Session_user_tracking_record_session_Ref",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jwt_api.session",
                    ),
                ),
                (
                    "Session_user_tracking_record_user_Ref",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="jwt_api.users"
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Session_stat_tracking_record",
        ),
        migrations.DeleteModel(
            name="Session_user_pool",
        ),
        migrations.DeleteModel(
            name="Users_stats",
        ),
    ]
