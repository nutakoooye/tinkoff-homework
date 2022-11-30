import argparse
import yaml

from server import ServerURL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Simple asynchronous distributed file storage'
    )
    parser.add_argument(
        "-p",
        action="store",
        dest="path",
        required=True,
        type=str,
        help="enter the path to the configuration file",
    )
    return parser.parse_args()


if __name__ == '__main__':
    CONFIG_PATH = parse_args().path

    with open(CONFIG_PATH, "r", encoding="UTF8") as f:
        config = yaml.safe_load(f)

        server = ServerURL(**config)
        server.run()
