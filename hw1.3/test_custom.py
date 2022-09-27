from unittest import TestCase
from log_parse import parse


class LoggingTestCase(TestCase):
    def test_ignore_files_and_www(self):
        self.assertEqual(parse(ignore_files=True, ignore_www=True),
                         [4, 3, 3, 3, 3]
                         )

    def test_ignore_www_and_url(self):
        self.assertEqual(
            parse(ignore_www=True, ignore_urls=["sys.mail.ru"]), [])

    def test_big_start_at(self):
        self.assertEqual(
            parse(start_at="18/Mar/2023 11:19:41"), [])

    def test_low_stop_at(self):
        self.assertEqual(
            parse(stop_at="18/Mar/2015 11:19:41"), [])

    def test_ignore_incorrect_url(self):
        self.assertEqual(
            parse(ignore_urls=["incorrect_url.com"]), [3, 3, 3, 2, 2])

    def test_slow_queries_ignore_www(self):
        self.assertEqual(
            parse(ignore_www=True, slow_queries=True),
            [61699, 53544, 42979, 27412, 26364]
        )

    def test_ignore_files_slow_queries(self):
        self.assertEqual(
            parse(ignore_files=True, slow_queries=True),
            [53544, 34054, 27412, 20431, 18757]
        )

    def test_with_complex_filter(self):
        self.assertEqual(
            parse(ignore_files=True,
                  start_at="18/Mar/2018 11:19:41",
                  stop_at="28/Mar/2018 11:19:40",
                  request_type="GET",
                  slow_queries=True,
                  ignore_urls=["sys.mail.ru"]
                  ),
            [53544, 50599, 20431, 966, 966]
        )
