from django import forms

from .models import Spider


class SpiderTestForm(forms.Form):
    spider = forms.ModelChoiceField(queryset=Spider.objects.all(), required=True)
    url = forms.URLField(required=True)

    def scrape(self):
        url = self.cleaned_data['url']
        spider = self.cleaned_data['spider']

        scrapy_settings = {
            'FEED_FORMAT': 'json',
            'FEED_EXPORT_ENCODING': 'utf-8',
            #        'FEED_URI': item_storage.name,
            'DNS_TIMEOUT': 5,
            'DOWNLOAD_TIMEOUT': 5,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 5,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
            'CLOSESPIDER_ITEMCOUNT': 1,
            'CLOSESPIDER_PAGECOUNT': 3,
            'CLOSESPIDER_TIMEOUT': 10,
        }

        """
        Run spider until a single item is recorded, saving the JSON result to string
        
        Set logging to DEBUG, save to string as well.
        
        return {
            'item': {},
            'url': '',
            'log': ''
        }
        """
