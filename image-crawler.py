#!/usr/bin/env python3
#
# image crawler
#
# the image crawler checks for new openstack ("cloud") images
# whenever a new image is detected all relevant information needed for
# maintaining an image catalog
#
# 2023-06-XX v0.4.0 christian.stelter@plusserver.com

import argparse
import sys
import os
# import logging
from loguru import logger
from crawler.core.config import config_read
from crawler.core.database import (
    database_connect,
    database_disconnect,
    database_initialize,
)
from crawler.core.exporter import export_image_catalog, export_image_catalog_all
from crawler.core.main import crawl_image_sources
from crawler.git.base import clone_or_pull, update_repository

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def main():
    logger.info("plusserver Image Crawler v0.4.0 started")

    working_directory = os.getcwd()
    program_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="checks cloud image repositories for new updates and"
        + " keeps track of all images within its sqlite3 database"
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
    parser.add_argument(
        "--init-db",
        action="store_true",
        required=False,
        help="initialize image catalog database",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        required=False,
        help="export only existing image catalog",
    )
    parser.add_argument(
        "--updates-only",
        action="store_true",
        required=False,
        help="check only for updates, do not export catalog",
    )
    args = parser.parse_args()

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

    image_source_catalog = config_read(sources_filename, "source catalog")
    if image_source_catalog is None:
        raise SystemExit("Unable to open image source catalog " + sources_filename)

    # initialize database when run with --init-db
    if args.init_db:
        database_initialize(config["database_name"], program_directory)
        sys.exit(0)

    # clone or update local repository when git is enabled
    if "remote_repository" in config:
        if "git_ssh_command" in config:
            git_ssh_command = config["git_ssh_command"]
        else:
            git_ssh_command = None
        if "branch" in config:
            working_branch = config["branch"]
        else:
            working_branch = main
        clone_or_pull(
            config["remote_repository"],
            config["local_repository"],
            working_branch,
            git_ssh_command,
        )
    else:
        logger.warning("No image catalog repository configured")

    # connect to database
    database = database_connect(config["database_name"])
    if database is None:
        logger.error("Could not open database %s" % config["database_name"])
        logger.error(
            'Run "./image-crawler.py --init-db" to create a new database OR config check your etc/config.yaml'
        )
        sys.exit(1)

    # crawl image sources when requested
    if args.export_only:
        logger.info("Skipping repository crawling")
        updated_sources = {}
    else:
        logger.info("Start repository crawling")
        updated_sources = crawl_image_sources(image_source_catalog, database)

    # export image catalog
    if args.updates_only:
        logger.info("Skipping catalog export")
    else:
        if config["local_repository"].startswith("/"):
            export_path = config["local_repository"]
        else:
            export_path = working_directory + "/" + config["local_repository"]

        if updated_sources:
            logger.info("Exporting catalog to %s" % export_path)
            export_image_catalog(
                database,
                image_source_catalog,
                updated_sources,
                config["local_repository"],
                config["template_path"],
            )
        else:
            if args.export_only:
                logger.info("Exporting all catalog files to %s" % export_path)
                export_image_catalog_all(
                    database,
                    image_source_catalog,
                    config["local_repository"],
                    config["template_path"],
                )

    # push changes to git repository when configured
    if "remote_repository" in config and updated_sources:
        update_repository(
            database, config["local_repository"], updated_sources, git_ssh_command
        )
    else:
        logger.info("No remote repository update needed.")

    database_disconnect(database)


if __name__ == "__main__":

    main()
