import unittest
from partybot import tools


class TestTools(unittest.TestCase):
    def test_array_join(self):
        arr = ['hello', 'word']
        res = tools.array_join(arr, ' ', lambda x: x.capitalize())
        self.assertEqual(res, 'Hello Word')
        arr = ['oh', 'I believe in yesterday']
        res = tools.array_join(arr, ', ', lambda x: x.capitalize())
        self.assertEqual(res, 'Oh, I believe in yesterday')
