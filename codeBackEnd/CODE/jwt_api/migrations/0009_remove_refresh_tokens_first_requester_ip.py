# Generated by Django 5.0.6 on 2024-07-02 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0008_users_devices"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="refresh_tokens",
            name="first_requester_ip",
        ),
    ]