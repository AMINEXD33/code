# Generated by Django 5.0.6 on 2024-07-03 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0010_alter_users_devices_device_ip_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="users_devices",
            name="is_pc",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="users_devices",
            name="is_phone",
            field=models.BooleanField(default=False),
        ),
    ]
