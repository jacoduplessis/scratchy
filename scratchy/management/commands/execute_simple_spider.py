from django.core.management.base import BaseCommand
from scratchy.tasks import run_spider

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('spider_id', type=int)

    def handle(self, *args, **options):
        spider_id = options['spider_id']

        self.stdout.write(f'Running spider with ID "{spider_id}"')
        run_spider(spider_id)
