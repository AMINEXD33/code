# Generated by Django 5.0.6 on 2024-08-16 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_api", "0039_alter_sessionmetricshardrecord_sessionmetric_sessionref"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sessionmetricshardrecord",
            name="sessionMetric_SessionRef",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="jwt_api.session"
            ),
        ),
    ]
