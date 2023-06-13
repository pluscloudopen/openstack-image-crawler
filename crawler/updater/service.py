from loguru import logger

from crawler.core.database import db_get_last_checksum, write_or_update_catalog_entry # db_get_last_checksum_fedora
from crawler.updater.ubuntu import ubuntu_update_check
from crawler.updater.debian import debian_update_check
from crawler.updater.alma import alma_update_check
from crawler.updater.flatcar import flatcar_update_check
from crawler.updater.fedora import fedora_update_check
from crawler.updater.rocky import rocky_update_check



def image_update_service(connection, source):
    updated_releases = []
    for release in source["releases"]:
        last_checksum = db_get_last_checksum(
            connection, source["name"], release["name"]
        )

        logger.debug("last_checksum:" + last_checksum)

        if "ubuntu" in release["imagename"]:
            catalog_update = ubuntu_update_check(release, last_checksum)
        elif "debian" in release["imagename"]:
            catalog_update = debian_update_check(release, last_checksum)
        elif "Alma" in release["imagename"]:
            catalog_update = alma_update_check(release, last_checksum)
        elif "flatcar" in release["imagename"]:
            catalog_update = flatcar_update_check(release, last_checksum)
        elif "Fedora" in release["imagename"]:
            catalog_update = fedora_update_check(release, last_checksum)
        elif "Rocky" in release["imagename"]:
            catalog_update = rocky_update_check(release, last_checksum)

        else:
            logger.error("Unsupported distribution " + source["name"] + " - please check your images-sources.yaml")
            raise SystemExit(1)
        if catalog_update:
            logger.info("Update found for " + source["name"] + " " + release["name"])
            logger.info("New release " + catalog_update["version"])
            # catalog_update anreichern mit _allen_ Daten für die DB
            catalog_update["distribution_name"] = source["name"]
            if "Fedora" in release["imagename"]:
                catalog_update["name"] = source["name"] + " " + catalog_update["release_id"]
                catalog_update["distribution_release"] = catalog_update["release_id"]
            else:
                catalog_update["name"] = source["name"] + " " + release["name"]
                catalog_update["distribution_release"] = release["name"]
            catalog_update["release"] = release["name"]

            write_or_update_catalog_entry(connection, catalog_update)
            updated_releases.append(release["name"])
        else:
            logger.info("No update found for " + source["name"] + " " + release["name"])

    return updated_releases
