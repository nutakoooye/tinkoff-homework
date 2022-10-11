import os
import re
import json
import time

from functools import wraps


def get_slug(string: str) -> str:
    slug = string.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    slug = re.sub(r"[-]+", "-", slug)
    return slug


def read_json(path: str) -> dict:
    with open(path) as f:
        templates = json.load(f)
        return templates


def write_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f)


def cache_is_obsolete(path: str, time_in_seconds: int) -> bool:
    time_created = os.path.getmtime(path)
    if time.time() - time_created > time_in_seconds:
        return True
    return False


def cached(ttl: int):
    def cached_inner(func):
        dir_path = ".tv_program_cache/"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        @wraps(func)
        def wrapper(url: str, params: dict[str, str]):
            file_name = get_slug(params["q"]) + ".json"
            path = dir_path + file_name

            if not os.path.exists(path) or cache_is_obsolete(path, ttl):
                g = func(url, params)
                if g:
                    write_json(path, g)
                return g
            else:
                return read_json(path)

        return wrapper

    return cached_inner
