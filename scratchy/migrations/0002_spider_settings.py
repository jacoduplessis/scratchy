# Generated by Django 3.0.3 on 2020-03-30 05:56

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scratchy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spider',
            name='settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Scrapy settings object for this spider only.'),
        ),
    ]
