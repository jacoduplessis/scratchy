import sqlite3
import tempfile

from django.contrib import admin
from django.db.models import OuterRef, Subquery, Count
from django.http.response import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.html import mark_safe

from .models import Spider, Execution, Item
from .tasks import run_spider


def dict_to_html_table(d):
    markup = '<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>'
    for k, v in d.items():
        markup += f'<tr><td>{k}</td><td>{v}</td></tr>'
    markup += '</tbody></table>'
    return mark_safe(markup)


class ExecutionInline(admin.TabularInline):
    model = Execution

    def num_items_scraped(self, obj):
        return obj.num_items

    fields = [
        'time_started',
        'num_items_scraped',

    ]
    readonly_fields = [
        'time_started',
        'num_items_scraped',

    ]
    max_num = 20
    extra = 0
    can_delete = False
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-time_started').annotate(num_items=Count('item'))


class SpiderAdmin(admin.ModelAdmin):

    def last_execution(self, obj):
        return obj.last_execution_time

    def last_finish(self, obj):
        return obj.last_finish_reason

    def num_executions(self, obj):
        return obj.num_executions

    def schedule_for_execution(self, request, qs):
        for obj in qs:
            run_spider.delay(obj.id)
        self.message_user(request, f'{len(qs)} spiders scheduled for execution')

    def set_active(self, request, qs):
        qs.update(active=True)
        n = qs.count()
        self.message_user(request, f'{n} spiders set as active')

    def set_inactive(self, request, qs):
        qs.update(active=False)
        n = qs.count()
        self.message_user(request, f'{n} spiders set as inactive')

    list_display = [
        'module',
        'id',
        'name',
        'active',
        'num_executions',
        'last_execution',
        'last_finish',
    ]

    list_filter = [
        'active',
    ]

    actions = [
        'schedule_for_execution',
        'set_active',
        'set_inactive',
    ]

    inlines = [
        ExecutionInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            last_execution_time=Subquery(Execution.objects.filter(spider_id=OuterRef('id')).order_by('-time_started').values('time_started')[:1]),
            last_finish_reason=Subquery(Execution.objects.filter(spider_id=OuterRef('id')).order_by('-time_started').values('stats__finish_reason')[:1]),
            num_executions=Count('execution'),
        )


class ExecutionAdmin(admin.ModelAdmin):

    def num_items(self, obj):
        return obj.num_items_scraped

    list_display = [
        'time_started',
        'spider',
        'time_ended',
        'responses',
        'num_items',
        'seconds',
        'finish_reason',
        'download_size',
        'download_markup',
    ]

    list_filter = [
        'spider',
    ]

    fields = [
        'spider',
        'time_started',
        'time_ended',
        'stats_table',
        'log',
    ]

    date_hierarchy = 'time_started'

    readonly_fields = [
        'spider',
        'time_started',
        'time_ended',
        'stats_table',
        'log',
    ]

    def stats_table(self, obj):
        return dict_to_html_table(obj.stats)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('spider').annotate(
            num_items_scraped=Count('item')
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/download/excel/',
                self.admin_site.admin_view(self.download('excel')),
                name='scratchy_execution_download_excel',
            ),
            path(
                '<int:pk>/download/sqlite/',
                self.admin_site.admin_view(self.download('sqlite')),
                name='scratchy_execution_download_sqlite',
            ),
        ]
        return custom_urls + urls

    def download(self, format):
        def view(request, pk):

            response = HttpResponse()
            execution = self.model.objects.select_related('spider').get(id=pk)
            extension = ''
            content_type = ''

            if format == 'excel':
                df = execution.items_as_df(stringify_datetime=True)
                df.to_excel(response, index=False)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                extension = 'xlsx'
            elif format == 'sqlite':
                df = execution.items_as_df()
                t = tempfile.NamedTemporaryFile()
                conn = sqlite3.connect(t.name)
                df.to_sql('items', conn, index=False)
                conn.close()
                response.write(t.read())
                t.close()
                extension = 'sqlite3'
                content_type = 'application/octet-stream'

            response['Content-Disposition'] = f'attachment; filename={execution.spider.name}_{execution.time_started.strftime("%Y-%m-%d")}.{extension}'
            response['Content-Type'] = content_type

            return response

        return view

    def download_markup(self, obj):
        return format_html(
            '<a class="button" download href="{}">Excel</a>&nbsp;'
            '<a class="button" download href="{}">SQLite</a>',
            reverse('admin:scratchy_execution_download_excel', args=[obj.pk]),
            reverse('admin:scratchy_execution_download_sqlite', args=[obj.pk]),
        )

    download_markup.short_description = 'Download Items'
    download_markup.allow_tags = True


class ItemAdmin(admin.ModelAdmin):

    def data_formatted(self, obj):
        return dict_to_html_table(obj.data)

    date_hierarchy = 'time_created'


readonly_fields = [
    'time_created',
    'spider',
    'execution',
    'data_formatted',
]

list_display = [
    'spider',
    'time_created',
]

list_filter = [
    'spider',
]


def get_queryset(self, request):
    return super().get_queryset(request).select_related('spider')


admin.site.register(Spider, SpiderAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Item, ItemAdmin)
