# Generated by Django 5.0.6 on 2024-08-28 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "jwt_api",
            "0044_alter_session_user_tracking_record_session_user_tracking_record_activity_ends_at_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="session_user_tracking_record",
            name="Session_user_tracking_record_errors",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="session_user_tracking_record",
            name="Session_user_tracking_record_submitions",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="session_user_tracking_record",
            name="Session_user_tracking_record_summarized_lines_of_code",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="session_user_tracking_record",
            name="Session_user_tracking_record_suspicious",
            field=models.TextField(default=""),
        ),
    ]
