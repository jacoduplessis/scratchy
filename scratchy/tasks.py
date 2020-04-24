from celery import shared_task
from .models import Spider as SpiderModel, Execution, Item
from django.utils.timezone import now
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.spider import iter_spider_classes
import tempfile
import json
import importlib
import os
from io import StringIO
import logging


@shared_task
def start_spiders():
    for spider in SpiderModel.objects.all():
        run_spider.delay(spider.id)


@shared_task
def run_spider(spider_id):
    spider = SpiderModel.objects.get(id=spider_id)
    execution = Execution.objects.create(spider_id=spider_id, time_started=now())

    item_storage = tempfile.NamedTemporaryFile(delete=False)

    scrapy_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_URI': item_storage.name,
        'DNS_TIMEOUT': 5,
        'DOWNLOAD_TIMEOUT': 5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }

    scrapy_settings.update(spider.settings)

    scrapy_spider_cls = None

    module = importlib.import_module(spider.module)

    for cls in iter_spider_classes(module):
        scrapy_spider_cls = cls
        break  # use first valid class in module

    if scrapy_spider_cls is None:
        raise RuntimeError(f'No valid spider class found in module {module}')

    process = CrawlerProcess(settings=None, install_root_handler=False)

    log_capture_string = StringIO()
    log_handler = logging.StreamHandler(log_capture_string)
    log_handler.setLevel(spider.log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    scrapy_logger = logging.getLogger('scrapy')
    scrapy_logger.addHandler(log_handler)
    spider_logger = logging.getLogger(scrapy_spider_cls.name)  # scrapy uses the spider name as logger id
    spider_logger.addHandler(log_handler)

    crawler = Crawler(scrapy_spider_cls, scrapy_settings)

    process.crawl(crawler)
    process.start()
    # blocks here

    log_contents = log_capture_string.getvalue()
    spider_logger.removeHandler(log_handler)
    scrapy_logger.removeHandler(log_handler)
    log_capture_string.close()

    execution.time_ended = now()
    execution.stats = crawler.stats._stats
    execution.log = log_contents
    execution.save()

    item_storage.seek(0)

    items = []
    for line in item_storage.readlines():
        item_data = json.loads(line)
        item = Item(spider_id=spider_id, execution=execution, data=item_data)
        items.append(item)

    Item.objects.bulk_create(items, batch_size=100)

    item_storage.close()
    os.remove(item_storage.name)
