# scratchy

The glue between Django, Scrapy and Celery.

## Usage

See test project for simple usage.

## Advice

- don't link to item model: process as you wish, then mark as processed
- processed items should be deleted on a periodic basis
- suggest running separate celery worker with task routing and `--max-tasks-per-child 1`

## Notes

- requires postgres for JSON column
- requires pandas + openpyxl for exporting to excel / sqlite
- tested with scrapy > 2
- items must be JSON serializable
- celery worker must restart after running a crawler process (CELERY_WORKER_MAX_TASKS_PER_CHILD=1)

## TODO

- admin screen to test scraper agains single URL
- fix SQLite export when data contains list (pandas to_sql)
- documentation
- scraper collections / projects
- add configurable settings globally / per project
- online scraper code
- scheduling
- timeout for execution
- add multiple crawlers to a crawler process when possible (times + logs may cross-contaminate)
