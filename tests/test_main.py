import unittest
import main
from datetime import datetime


def stod(string):
    return datetime.strptime(string, '%d.%m.%Y %H:%M')


class TestTools(unittest.TestCase):
    def test_get_hours_minutes(self):
        h, m = main.get_hours_minutes('10')
        self.assertEqual(h, 10)
        self.assertEqual(m, 0)
        h, m = main.get_hours_minutes('10:01')
        self.assertEqual(h, 10)
        self.assertEqual(m, 1)
        h, m = main.get_hours_minutes(' 10 : 05 ')
        self.assertEqual(h, 10)
        self.assertEqual(m, 5)
        h, m = main.get_hours_minutes('10:1')
        self.assertEqual(h, 10)
        self.assertEqual(m, 1)

    def test_extract_time(self):
        req_time = stod('10.06.2021 00:00')
        test_str = [
            'с 15:35',
            'с 12 до 15',
            '12 - 15',
            '12-15',
            '12:00-15:00',
            '12-1',
            'dsfa'
        ]
        results = [
            (stod('10.06.2021 15:35'), stod('10.06.2021 23:59')),
            (stod('10.06.2021 12:00'), stod('10.06.2021 15:00')),
            (stod('10.06.2021 12:00'), stod('10.06.2021 15:00')),
            (stod('10.06.2021 12:00'), stod('10.06.2021 15:00')),
            (stod('10.06.2021 12:00'), stod('10.06.2021 15:00')),
            (stod('10.06.2021 12:00'), stod('11.06.2021 1:00')),
            None
        ]
        for i in range(len(test_str)):
            self.assertEqual(main.extract_time(req_time, test_str[i]), results[i])


if __name__ == '__main__':
    unittest.main()
