# Generated by Django 5.0.6 on 2024-08-16 18:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0034_sessionmetricshardrecord"),
    ]

    operations = [
        migrations.AddField(
            model_name="sessionmetricshardrecord",
            name="sessionMetric_SessionRef",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="jwt_api.session",
            ),
            preserve_default=False,
        ),
    ]