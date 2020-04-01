from scratchy.tasks import run_spider
from django.test import LiveServerTestCase
from scratchy.models import Spider, Execution, Item


class TestSimpleScaping(LiveServerTestCase):
    port = 9009

    def setUp(self):
        self.spider = Spider.objects.create(module='scratchy_test.spider', active=True)

    def test_spider_execution_saves_items(self):
        run_spider(self.spider.id)

        execution = Execution.objects.first()
        self.assertEqual(execution.spider_id, self.spider.id)
        self.assertEqual(execution.finish_reason, 'finished')

        num_items = Item.objects.all().count()
        self.assertEqual(num_items, 3)
