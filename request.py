import requests
import json
from html.parser import HTMLParser
import datetime


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


def kudago_dates(dates, date_from, date_to):
    for el in dates:
        print(el)
        try:
            start = datetime.datetime.utcfromtimestamp(el['start'])
        except:
            start = date_from

        try:
            end = datetime.datetime.utcfromtimestamp(el['end'])
        except:
            end = date_to
        if start >= date_from:
            return start, end
    return date_from, date_to


def kudago(user_request):
    categories = ['party']
    location = {
        'москва': 'msk'
    }
    fields = ['dates', 'title', 'place', 'location', 'price', 'is_free', 'site_url', 'age_restriction']
    print(user_request)
    request_link = f'https://kudago.com/public-api/v1.4/events/?lang=ru' \
                   f'&fields={",".join(fields)}&expand=&order_by=&text_format=&ids=' \
                   f'&location={location[user_request["city"]]}' \
                   f'&actual_since={user_request["date_from"].timestamp()}' \
                   f'&actual_until={user_request["date_to"].timestamp()}&is_free=' \
                   f'&categories={",".join(categories)}&lon=&lat=&radius='
    print(request_link)
    response = requests.get(request_link)
    messages = response.json()
    print(messages)
    result = []
    count = 1
    for event in messages['results']:
        res = f'{count}. {event["title"].capitalize()}. Подробнее по [ссылке]({event["site_url"]})\n'
        start, end = kudago_dates(event['dates'], user_request['date_from'], user_request['date_to'])
        res += f'{start.strftime("%d.%m %H:%M")} - {end.strftime("%d.%m %H:%M")}\n'
        res += f'Стоимость: {event["price"].capitalize()}. {event["age_restriction"]}\n\n'
        result.append(res)
        count += 1

    return result
