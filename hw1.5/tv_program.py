import requests
import sys
from typing import Any
from tv_program_model import TVProgram, print_tv_program
from decorators import cached


def get_name_from_cmd() -> str:
    params = " ".join(sys.argv[1:])
    return params


@cached(ttl=5 * 60)
def get_dict_tv_program(url: str, params: dict[str, str]) -> dict | Any:
    try:
        response = requests.get(url, params)
        return response.json()
    except requests.exceptions.RequestException:
        return None


URL = "https://api.tvmaze.com/singlesearch/shows"

if __name__ == "__main__" or __name__ == "tv_program":
    name = get_name_from_cmd()
    tv_dict = get_dict_tv_program(URL, {"q": name})
    if tv_dict is None:
        print("Program not found")
    else:
        tv_program = TVProgram(**tv_dict)
        print_tv_program(tv_program)
