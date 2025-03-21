# Generated by Django 5.1.7 on 2025-03-17 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_application_application_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='application_deadline',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='application_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='duration',
            field=models.CharField(blank=True, help_text="e.g., '6 months', '1 year'", max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='notification_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
