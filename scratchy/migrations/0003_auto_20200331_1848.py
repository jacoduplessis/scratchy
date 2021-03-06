# Generated by Django 3.0.4 on 2020-03-31 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scratchy', '0002_spider_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='execution',
            name='log',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='spider',
            name='log_level',
            field=models.CharField(choices=[('CRITICAL', 'Critical'), ('ERROR', 'Error'), ('WARNING', 'Warning'), ('INFO', 'Info'), ('DEBUG', 'Debug'), ('NOTSET', 'Not Set')], default='INFO', max_length=20),
        ),
    ]
