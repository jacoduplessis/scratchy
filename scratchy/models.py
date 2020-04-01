from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import filesizeformat
import logging


class Spider(models.Model):
    """
    CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


_nameToLevel = {
    'CRITICAL': CRITICAL,
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}
    """

    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'

    LOG_LEVEL_CHOICES = (
        (CRITICAL, 'Critical'),
        (ERROR, 'Error'),
        (WARNING, 'Warning'),
        (INFO, 'Info'),
        (DEBUG, 'Debug'),
        (NOTSET, 'Not Set')
    )

    time_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, blank=True)
    module = models.CharField(max_length=200, unique=True)
    active = models.BooleanField(default=False, db_index=True)
    settings = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder, help_text='Scrapy settings object for this spider only.')
    log_level = models.CharField(max_length=20, default=INFO, choices=LOG_LEVEL_CHOICES)

    def __str__(self):
        return f'{self.module}'

    def get_file_name(self):
        return self.module.split('.')[-1]


class Execution(models.Model):
    spider = models.ForeignKey(Spider, on_delete=models.CASCADE)
    stats = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True)

    @property
    def finish_reason(self):
        return self.stats.get('finish_reason', '---')

    @property
    def download_size(self):
        b = self.stats.get('downloader/response_bytes', 0)
        return filesizeformat(b)

    @property
    def seconds(self):
        return int(self.stats.get('elapsed_time_seconds', 0))


class Item(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    spider = models.ForeignKey(Spider, on_delete=models.CASCADE)
    execution = models.ForeignKey(Execution, null=True, on_delete=models.SET_NULL)
    data = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    processed = models.BooleanField(default=False, db_index=True)
