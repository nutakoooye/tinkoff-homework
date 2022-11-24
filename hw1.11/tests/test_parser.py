from unittest import TestCase
from parser import YoutubeHeaderParser, YMusicHeaderParser, HabrHeaderParser
import os


class TestYMusicHeaderParser(TestCase):
    def test_parser(self):
        path = os.getcwd()
        with open(path + "/tests/static/YandexMusic.html", "r") as page:
            parser = YMusicHeaderParser()
            header = parser.parse_header(page)
            self.assertEqual(header, "Megalomaniac")


class TestYoutubeHeaderParser(TestCase):
    def test_parser(self):
        path = os.getcwd()
        with open(path + "/tests/static/YouTube.html", "r") as page:
            parser = YoutubeHeaderParser()
            header = parser.parse_header(page)
            self.assertEqual(
                header,
                "Месяц с Google Pixel 7 Pro и Pixel Watch — все плюсы и минусы!",
            )


class TestHabrHeaderParser(TestCase):
    def test_parser(self):
        path = os.getcwd()
        with open(path + "/tests/static/Habr.html", "r") as page:
            parser = HabrHeaderParser()
            header = parser.parse_header(page)
            self.assertEqual(header, "Зачем писать на C++ в 2022 году?")
