#!/usr/bin/env python3
#
# crawl-back-eval
#
# evaluation of a historian replacement
#
# 2023-06-18 v0.0.2 christian.stelter@plusserver.com

import argparse
import sys
import os
from loguru import logger
from crawler.core.config import config_read
from crawler.core.database import (
    database_connect,
    database_disconnect
)
from crawler.core.main import crawl_back_image_sources


def main():
    working_directory = os.getcwd()
    program_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="tests crawl back functions"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=False,
        help="specify the config file to be used (default: <path_to_crawler_dir>/etc/config.yaml)",
    )
    parser.add_argument(
        "--sources",
        type=str,
        required=False,
        help="specify the sources file to be used - overrides value from config file",
    )
    args = parser.parse_args()

    # static for debug
    log_level = "DEBUG"
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}:{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    logger.remove()
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)

    logger.info("crawl back evaluator v0.0.2 started")

    # read configuration
    if args.config is not None:
        config_filename = args.config
    else:
        # default
        config_filename = program_directory + "/etc/config.yaml"

    config = config_read(config_filename, "configuration")
    if config is None:
        logger.error("ERROR: Unable to open config " + config_filename)
        raise SystemExit(1)

    # read the image sources
    if args.sources is not None:
        sources_filename = args.sources
    else:
        sources_filename = config["sources_name"]

    # connect to database
    database = database_connect(config["database_name"])
    if database is None:
        logger.error("Could not open database %s" % config["database_name"])
        logger.error(
            'Run "./image-crawler.py --init-db" to create a new database OR config check your etc/config.yaml'
        )
        sys.exit(1)

    image_source_catalog = config_read(sources_filename, "source catalog")
    if image_source_catalog is None:
        logger.error("Unable to open image source catalog " + sources_filename)
        raise SystemExit(1)

    crawl_back_image_sources(image_source_catalog, database)

    database_disconnect(database)

if __name__ == "__main__":

    main()
