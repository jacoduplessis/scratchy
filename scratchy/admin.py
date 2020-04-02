from django.contrib import admin
from django.db.models import OuterRef, Subquery, Count
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


class ItemAdmin(admin.ModelAdmin):

    def data_formatted(self, obj):

        return dict_to_html_table(obj.data)



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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('spider')


admin.site.register(Spider, SpiderAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Item, ItemAdmin)
