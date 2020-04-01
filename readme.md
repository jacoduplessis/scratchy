# scratchy

The glue between Django, Scrapy and Celery.

## Usage

See test for simple usage.

## Notes

- items must be JSON serializable
- celery worker must restart after running a spider (CELERY_WORKER_MAX_TASKS_PER_CHILD=1)

## TODO

documentation
scraper collections / projects
add configurable settings globally / per project
online scraper code
scheduling
timeout for execution
add multiple crawlers to a crawler process when possible
