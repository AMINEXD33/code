# Generated by Django 5.0.6 on 2024-07-01 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0004_refresh_tokens_alter_users_user_email_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="refresh_tokens",
            name="first_requester_ip",
            field=models.CharField(max_length=160),
        ),
    ]