"""Request to https://kudago.com/ for events"""
import datetime
import requests
import logging

LOCATION = {
    'москва': 'msk'
}
LINK = 'https://kudago.com/public-api/v1.4/events/?lang=ru' \
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
    """
    Checks if date in range between date_from and date_to.

    :param date: Date to check
    :param datetime.date date_from: Begin of date range
    :param datetime.date date_to: End of date range

    :return: bool
    """
    if not isinstance(date, datetime.date):
        return False

    return date_from <= date <= date_to


def get_dates(dates, date_from, date_to):
    """
    Extract dates to show from array of dates from kudago request.

    :param list dates: List of dates from kudago request
    :param datetime.date date_from: User request start date
    :param datetime.date date_to: User request end date
    :return: Two dates if there is correct ones, otherwise - two empty strings
    """
    for element in dates:
        try:
            start = datetime.datetime.utcfromtimestamp(element['start'])
        except OSError as error:
            start = ''
        try:
            end = datetime.datetime.utcfromtimestamp(element['end'])
        except OSError as error:
            end = ''

        if in_range(start, date_from, date_to) or end > date_to:
            return start, end
    return '', ''


def create_dates(date_from, date_to):
    """
    Creates string from dates to show.

    :param date_from: Range start
    :param date_to: Range end
    :return: string
    """
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
    """
    Checks if string has any numbers in it.

    :param string: String to check
    :return: bool
    """
    if string is str:
        return any(char.isdigit() for char in string)
    return False


def create_price(event):
    """
    Creates price string to show.

    :param dict event: Event from kudago
    :return: Price string
    :rtype: string
    """
    if has_number(event['is_free']):
        price = event['is_free'] + '. ' + event['price']
    else:
        if event['is_free'] == 'true' and not has_number(event['price']):
            price = 'Вход свободный.'
        else:
            price = event['price']
    return price


def parse_response(message, req):
    """
    Parses request from kudago.

    :param dict message: Response from kudago
    :param req: User request
    :return: List of messages to show
    :rtype: list
    """
    result = []
    count = 1
    for event in message['results']:
        try:
            title = event['title'].capitalize()
            url = event["site_url"]
            date_from, date_to = get_dates(event['dates'], req['date_from'], req['date_to'])
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
        except Exception as error:
            pass
        count += 1
    return result


def send_request(user_request):
    """
    Send request to kudago.com and parse response.

    :param dict user_request: User request
    :return: List of messages with events to show
    :rtype: list
    """
    fields = [
        'dates',
        'title',
        'place',
        'location',
        'price',
        'is_free',
        'site_url',
        'age_restriction'
    ]
    date_to = user_request['date_to'].timestamp()
    date_from = user_request['date_from'].timestamp()
    request_link = LINK.format(
        fields=','.join(fields),
        location=LOCATION[user_request['city']],
        date_from=date_from,
        date_to=date_to
    )
    logging.info(f'[KUDAGO] Requests to {request_link}.')
    response = requests.get(request_link)
    messages = response.json()
    result = parse_response(messages, user_request)

    return result
