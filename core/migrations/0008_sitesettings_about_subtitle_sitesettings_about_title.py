# Generated by Django 5.1.7 on 2025-03-13 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_whatwedo_sitesettings_what_we_do_subtitle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='about_subtitle',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='about_title',
            field=models.CharField(default='About Us', max_length=200),
        ),
    ]
