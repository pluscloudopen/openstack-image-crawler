#!/usr/bin/env python3
#
# image crawler
#
# the image crawler checks for new openstack ("cloud") images
# whenever a new image is detected all relevant information needed for
# maintaining an image catalog
#
# 2022-09-19 v0.1 christian.stelter@plusserver.com

import argparse
import os

from crawler.core.config import config_read
from crawler.core.database import database_connect, database_disconnect, database_initialize
from crawler.core.exporter import export_image_catalog
from crawler.updater.service import image_update_service
from crawler.git.base import clone_or_pull, update_repository


def main():
    # first_run ??
    # create missing directories (exports)

    print("\nplusserver Image Crawler v0.1\n")

    working_directory = os.getcwd()

    parser = argparse.ArgumentParser(description='checks cloud image repositories for new updates and keeps track of all images within its sqlite3 database')
    parser.add_argument('--config', type=str, required=False,
                        help='specify the config file to be used (default: etc/config.yaml)')
    parser.add_argument('--sources', type=str, required=False,
                        help='specify the sources file to be used - overrides value from config file')
    parser.add_argument('--init-db', action='store_true', required=False,
                        help='initialize image catalog database')
    parser.add_argument('--export-only', action='store_true', required=False,
                        help='export only existing image catalog')
    parser.add_argument('--updates-only', action='store_true', required=False,
                        help='check only for updates, do not export catalog')
    args = parser.parse_args()

    if args.config is not None:
        config_filename = args.config
    else:
        # default
        config_filename = "etc/config.yaml"

    config = config_read(config_filename, "configuration")
    if config is None:
        raise SystemExit("ERROR: Unable to open config " + config_filename)

    if args.init_db:
        database_initialize(config['database_name'])
        exit(0)

    # pprint(config)
    if 'remote_repository' in config:
        clone_or_pull(config['remote_repository'], config['local_repository'])
    else:
        print("No image catalog repository configured")

    if args.sources is not None:
        sources_filename = args.sources
    else:
        sources_filename = config['sources_name']

    image_source_catalog = config_read(sources_filename, "source catalog")
    if image_source_catalog is None:
        raise SystemExit("Unable to open image source catalog " + sources_filename)

    # pprint(image_source_catalog)

    database = database_connect(config['database_name'])
    if database is None:
        print("ERROR: Could not open database %s" % config['database_name'])
        exit(1)

    if args.export_only:
        print("\nSkipping repository crawling")
    else:
        print("\nStart repository crawling")
        for source in image_source_catalog['sources']:
            print("\nChecking updates for Distribution " + source['name'])
            image_update_service(database, source)

    if args.updates_only:
        print("\nSkipping catalog export")
    else:
        print("\nExporting catalog to %s/%s" % (working_directory, config['local_repository']))
        export_image_catalog(database, image_source_catalog, config['local_repository'])

    if 'remote_repository' in config:
        update_repository(config['local_repository'])

    database_disconnect(database)


if __name__ == "__main__":
    main()
