import requests
import datetime

KUDAGO_LOACTION = {
    'москва': 'msk'
}
KUDAGO_LINK = 'https://kudago.com/public-api/v1.4/events/?lang=ru' \
              '&fields={fields}&order_by=' \
              '&location={location}' \
              '&actual_since={date_from}' \
              '&actual_until={date_to}' \
              '&categories=party'
RESPONSE = '''{number}. {title}.
Подробнее по [ссылке]({url})..
{dates}
{price}. {age}\n'''
ERROR_RESPONSE = 'При обработке запроса произошла ошибка. Попробуйте еще раз.'


def in_range(date, date_from, date_to):
    if not isinstance(date, datetime.date):
        return False

    return date_from <= date <= date_to


def kudago_dates(dates, date_from, date_to):
    for el in dates:
        try:
            start = datetime.datetime.utcfromtimestamp(el['start'])
        except Exception as e:
            start = ''
        try:
            end = datetime.datetime.utcfromtimestamp(el['end'])
        except Exception as e:
            end = ''

        if in_range(start, date_from, date_to) or end > date_to:
            return start, end
    return '', ''


def create_dates(date_from, date_to):
    if date_to == '' and date_from == '':
        return ''
    if date_from == date_to:
        return date_to.strftime("%d.%m %H:%M")
    if date_to == '':
        return f'С {date_from.strftime("%d.%m %H:%M")}'
    if date_from == '':
        return f'До {date_from.strftime("%d.%m %H:%M")}'
    return f'{date_from.strftime("%d.%m %H:%M")} -- {date_to.strftime("%d.%m %H:%M")}'


def has_number(string):
    if string is str:
        return any(char.isdigit() for char in string)
    return False


def create_price(event):
    if has_number(event['is_free']):
        price = event['is_free'] + '. ' + event['price']
    else:
        if event['is_free'] == 'true' and not has_number(event['price']):
            price = 'Вход свободный.'
        else:
            price = event['price']
    return price


def kudago_parse_response(message, user_request):
    result = []
    count = 1
    for event in message['results']:
        try:
            title = event['title'].capitalize()
            url = event["site_url"]
            date_from, date_to = kudago_dates(event['dates'], user_request['date_from'], user_request['date_to'])
            dates = create_dates(date_from, date_to)
            price = create_price(event)
            age = event['age_restriction']
            response_message = RESPONSE.format(
                number=count,
                title=title,
                url=url,
                dates=dates,
                price=price,
                age=age
            )
            result.append(response_message)
        except Exception as e:
            pass
        count += 1
    return result


def kudago(user_request):
    fields = ['dates', 'title', 'place', 'location', 'price', 'is_free', 'site_url', 'age_restriction']
    date_to = user_request['date_to'].timestamp()
    date_from = user_request['date_from'].timestamp()
    request_link = KUDAGO_LINK.format(
        fields=','.join(fields),
        location=KUDAGO_LOACTION[user_request['city']],
        date_from=date_from,
        date_to=date_to
    )
    response = requests.get(request_link)
    messages = response.json()
    result = kudago_parse_response(messages, user_request)

    return result
