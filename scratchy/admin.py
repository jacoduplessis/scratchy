from django.contrib import admin
from django.db.models import OuterRef, Subquery, Count
from django.utils.html import mark_safe
from .models import Spider, Execution, Item
from .tasks import run_spider


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

    def most_recent_execution(self, obj):
        return obj.most_recent_execution_time_started

    def schedule_for_execution(self, request, qs):

        for obj in qs:
            run_spider.delay(obj.id)
        self.message_user(request, f'{len(qs)} spiders scheduled for execution')


    list_display = [
        'module',
        'id',
        'name',
        'active',
        'most_recent_execution',
    ]

    list_filter = [
        'active',
    ]

    actions = [
        'schedule_for_execution',
    ]

    inlines = [
        ExecutionInline,
    ]

    def get_queryset(self, request):
        subquery = Subquery(
            Execution.objects.filter(spider_id=OuterRef('id')).order_by('-time_started').values('time_started')[:1]
        )

        qs = super().get_queryset(request)
        return qs.annotate(most_recent_execution_time_started=subquery)


class ExecutionAdmin(admin.ModelAdmin):

    def num_items(self, obj):
        return obj.num_items_scraped

    list_display = [
        'time_started',
        'spider',
        'time_ended',
        'num_items',
        'seconds',
        'finish_reason',
        'download_size',
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

    readonly_fields = [
        'spider',
        'time_started',
        'time_ended',
        'stats_table',
        'log',
    ]

    def stats_table(self, obj):

        markup = '<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>'
        for k, v in obj.stats.items():
            markup += f'<tr><td>{k}</td><td>{v}</td></tr>'
        markup += '</tbody></table>'
        return mark_safe(markup)


    def get_queryset(self, request):

        qs = super().get_queryset(request)
        return qs.select_related('spider').annotate(
            num_items_scraped=Count('item')
        )


class ItemAdmin(admin.ModelAdmin):

    def data_formatted(self, obj):
        markup = '<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>'
        for k, v in obj.data.items():
            markup += f'<tr><td>{k}</td><td>{v}</td></tr>'
        markup += '</tbody></table>'
        return mark_safe(markup)

    readonly_fields = [
        'spider',
        'execution',
        'data_formatted',
    ]


admin.site.register(Spider, SpiderAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Item, ItemAdmin)
