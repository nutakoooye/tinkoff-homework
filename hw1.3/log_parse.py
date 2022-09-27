import re
from datetime import datetime
from urllib.parse import urlparse

LOG_FILE_NAME = 'log.log'


class RequestLogParser:
    def __init__(self, log_str: str):
        self.request_date = None
        self.request_type = None
        self.request = None
        self.protocol = None
        self.response_code = None
        self.response_time = None
        self.parse(log_str)

    @staticmethod
    def __get_row_parts(log_str: str) -> dict:
        """
        returns parts of the log as strings
        """
        row_parts = dict()
        row_parts['request_date'] = re.search(r'(?<=\[)[\d\D]+(?=])',
                                              log_str)[0]
        row_parts['request_type'] = re.search(r'(?<=\")[A-Z]+', log_str)[0]
        row_parts['request'] = re.search(r'(?<=\s)https?://[^\s]+', log_str)[0]
        row_parts['protocol'] = re.search(r'HTTP.+(?=")', log_str)[0]
        row_parts['response_code'] = re.search(r'(?<= )\d{3}(?= )', log_str)[0]
        row_parts['response_time'] = re.search(r'(?<= )\d+$', log_str)[0]
        return row_parts

    def parse(self, log_str: str):
        row_log_parts = self.__get_row_parts(log_str)
        self.request_date = datetime.strptime(
            row_log_parts['request_date'],
            '%d/%b/%Y %H:%M:%S'
        )
        self.request_type = row_log_parts['request_type']
        self.request = urlparse(row_log_parts['request'])
        self.protocol = row_log_parts['protocol']
        self.response_code = row_log_parts['response_code']
        self.response_time = int(row_log_parts['response_time'])

    def is_file(self) -> bool:
        if '.' in self.request.path:
            return True
        return False

    def is_match(self,
                 ignore_files=False,
                 ignore_urls=[],
                 start_at=None,
                 stop_at=None,
                 request_type=None, ) -> bool:
        """
        check if the log satisfies the given parameters
        """
        if ignore_files and self.is_file():
            return False
        if ignore_urls and self.request.netloc in ignore_urls:
            return False
        if start_at and self.request_date < \
                datetime.strptime(start_at, '%d/%b/%Y %H:%M:%S'):
            return False
        if stop_at and self.request_date > \
                datetime.strptime(stop_at, '%d/%b/%Y %H:%M:%S'):
            return False
        if request_type and self.request_type != request_type:
            return False
        return True


def is_correct_log(log_str: str) -> bool:
    match = re.fullmatch(
        r'^\[\d\d/[a-zA-Z]{3}/\d{4} \d\d:\d\d:\d\d] \"[A-Z]+ '
        r'https?[\w\W]+ HTTPS?/\d\.\d\" \d{3} \d+$',
        log_str
    )
    return bool(match)


def del_www(log_str:str) -> str:
    return log_str.replace('www.', '', 1)


def get_url_dict(ignore_files, ignore_urls, start_at, stop_at, request_type,
                 ignore_www) -> {str: list}:
    """
    returns a dictionary with keys as urls
    and list values with query response time
    """
    url_count_dict = dict()
    with open(LOG_FILE_NAME, 'r', encoding='utf-8') as file:
        for line in file:
            log_str = line.strip()
            if is_correct_log(log_str):
                if ignore_www:
                    log_str = del_www(log_str)
                log = RequestLogParser(log_str)
                if log.is_match(ignore_files, ignore_urls, start_at,
                                stop_at, request_type):
                    key = log.request.netloc + log.request.path
                    if key in url_count_dict:
                        url_count_dict[key].append(log.response_time)
                    else:
                        url_count_dict[key] = [log.response_time]
    return url_count_dict


def get_five_common(url_count_dict: dict):
    sorted_tuples = sorted(url_count_dict.items(),
                           key=lambda item: len(item[1]), reverse=True)
    top_five_list = []
    for url_tuple in sorted_tuples[:5]:
        top_five_list.append(len(url_tuple[1]))
    return top_five_list


def get_five_slow(url_count_dict):
    response_time_list = []
    for value in url_count_dict.values():
        response_time_list.append(int(sum(value) / len(value)))
    response_time_list.sort(reverse=True)
    return response_time_list[:5]


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
) -> list:
    url_count_dict = get_url_dict(ignore_files, ignore_urls, start_at, stop_at,
                                  request_type, ignore_www)
    if slow_queries:
        top_five = get_five_slow(url_count_dict)
    else:
        top_five = get_five_common(url_count_dict)
    return top_five
