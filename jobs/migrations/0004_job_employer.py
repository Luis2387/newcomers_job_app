# Generated by Django 3.2.25 on 2024-10-16 03:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20241015_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='employer',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='jobs.employer'),
            preserve_default=False,
        ),
    ]
