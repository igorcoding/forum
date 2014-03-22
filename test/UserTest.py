import unittest
import requests


class UserTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost:8200/user/"

    def test_details(self):
        self.url += "details/"
        r = requests.get(self.url)
        print r.text


if __name__ == '__main__':
    unittest.main()