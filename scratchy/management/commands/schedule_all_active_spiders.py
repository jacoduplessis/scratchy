from django.core.management.base import BaseCommand
from scratchy.models import Spider
from scratchy.tasks import run_spider


class Command(BaseCommand):

    def handle(self, *args, **options):
        for spider in Spider.objects.filter(active=True):
            self.stdout.write(f'scheduling spider module {spider.module}')
            run_spider.delay(spider.id)
