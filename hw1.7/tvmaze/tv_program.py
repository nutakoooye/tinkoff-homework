import requests
from typing import Any
from .tv_program_model import TVProgram
from .decorators import cached


@cached(ttl=5 * 60)
def get_dict_tv_program(url: str, name: str) -> dict | Any:
    params = {"q": name}
    try:
        response = requests.get(url, params)
        return response.json()
    except requests.exceptions.RequestException:
        return None


URL = "https://api.tvmaze.com/singlesearch/shows"


def get_tv_program(name: str) -> TVProgram:
    tv_dict = get_dict_tv_program(URL, name)
    if tv_dict:
        program = TVProgram(**tv_dict)
        return program
    else:
        raise ValueError
