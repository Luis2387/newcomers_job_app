# Generated by Django 3.2.25 on 2024-11-20 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_remove_resume_jobseeker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='level',
        ),
    ]
