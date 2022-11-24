import argparse
from urllib.parse import urlparse

from parser import YoutubeHeaderParser, HabrHeaderParser, YMusicHeaderParser
from parser import Context

ALOWED_SITES = {
    "habr.com": HabrHeaderParser,
    "www.youtube.com": YoutubeHeaderParser,
    "music.yandex.ru": YMusicHeaderParser,
    "music.yandex.by": YMusicHeaderParser,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='parser titles for YouTube, YandexMusic and Habr'
    )
    parser.add_argument(
        "-l",
        action="store",
        dest="link",
        required=True,
        type=str,
        help="enter the url for parsing the header",
    )
    return parser.parse_args()


URL = parse_args().link

if __name__ == '__main__':
    urlp = urlparse(URL)
    netloc = urlp.netloc

    parser = ALOWED_SITES[netloc]
    context = Context(parser())

    print(context.parse_header(URL))
