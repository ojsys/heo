from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='value',
            field=models.CharField(
                default='0',
                max_length=50,
                help_text="The number or stat to display on the website, e.g. '500+' or '₦75M+'"
            ),
        ),
        migrations.AddField(
            model_name='achievement',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Tick to show this stat on the website; untick to hide it'
            ),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='title',
            field=models.CharField(
                max_length=100,
                help_text="Short label shown below the number, e.g. 'Students Supported'"
            ),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='Optional longer description (not shown on homepage)'
            ),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='icon',
            field=models.CharField(
                max_length=100,
                help_text="Font Awesome icon class, e.g. 'fas fa-graduation-cap'"
            ),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Display order — lower numbers appear first'
            ),
        ),
        migrations.AlterModelOptions(
            name='achievement',
            options={
                'ordering': ['order'],
                'verbose_name': 'Impact Statistic',
                'verbose_name_plural': 'Impact Statistics (Homepage Numbers)',
            },
        ),
    ]
