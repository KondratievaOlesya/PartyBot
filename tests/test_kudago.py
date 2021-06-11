import unittest
from partybot import kudago
from datetime import datetime
import datetime as dt


class TestKudago(unittest.TestCase):
    def test_in_range(self):
        date_from = datetime.strptime('10.06.2021 00:00', '%d.%m.%Y %H:%M')
        date_to = date_from + dt.timedelta(days=1)
        self.assertFalse(kudago.in_range('', date_from, date_to))
        self.assertTrue(kudago.in_range(datetime.strptime('10.06.2021 12:00', '%d.%m.%Y %H:%M'), date_from, date_to))
        date_to = datetime.strptime('02.01.2022 00:00', '%d.%m.%Y %H:%M')
        self.assertTrue(kudago.in_range(datetime.strptime('01.01.2022 12:00', '%d.%m.%Y %H:%M'), date_from, date_to))

    def test_has_number(self):
        self.assertTrue(kudago.has_number('dasdasd1'))
        self.assertTrue(kudago.has_number('1231'))
        self.assertFalse(kudago.has_number('dasdasd'))
        self.assertFalse(kudago.has_number('null'))
        self.assertFalse(kudago.has_number('false'))
        self.assertFalse(kudago.has_number(False))
        self.assertFalse(kudago.has_number(True))
        self.assertTrue(kudago.has_number('вход бесплатный, депозит от 500 до 700 рублей на человека в баре'))

    def test_create_price(self):
        event = {
            'price': 'вход бесплатный, депозит от 500 до 700 рублей на человека в баре',
            'is_free': True
        }
        self.assertEqual(
            kudago.create_price(event),
            'вход бесплатный, депозит от 500 до 700 рублей на человека в баре'
        )
        event['price'] = 'null'
        event['is_free'] = True
        self.assertEqual(kudago.create_price(event), 'Вход свободный')
        event['is_free'] = False
        self.assertEqual(kudago.create_price(event), 'null')
        event['is_free'] = 'в бар вход бесплатный, депозит от 500'
        self.assertEqual(kudago.create_price(event), 'в бар вход бесплатный, депозит от 500. null')


if __name__ == '__main__':
    unittest.main()
