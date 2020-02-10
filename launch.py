from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


def main(config_file, restart):
    print("main begin")
    cparser = ConfigParser()
    print("parser created")
    cparser.read(config_file)
    print("config file successfully read")
    config = Config(cparser)
    print("some other config")
    
    config.cache_server = get_cache_server(config, restart)
    print("cache server obtained")

    crawler = Crawler(config, restart)
    print("Crawler created")
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
