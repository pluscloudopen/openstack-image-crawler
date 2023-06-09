from crawler.core.database import db_get_last_checksum, write_or_update_catalog_entry

from crawler.updater.ubuntu import ubuntu_update_check
from crawler.updater.debian import debian_update_check
from crawler.updater.alma import alma_update_check
from crawler.updater.flatcar import flatcar_update_check


def image_update_service(connection, source):
    updated_releases = []
    for release in source["releases"]:
        last_checksum = db_get_last_checksum(
            connection, source["name"], release["name"]
        )

        print("image_update_service/last_checksum:" + last_checksum)

        if "ubuntu" in release["imagename"]:
            catalog_update = ubuntu_update_check(release, last_checksum)
        elif "debian" in release["imagename"]:
            catalog_update = debian_update_check(release, last_checksum)
        elif "alma" in release["imagename"]:
            catalog_update = alma_update_check(release, last_checksum)
        elif "flatcar" in release["imagename"]:
            catalog_update = flatcar_update_check(release, last_checksum)
        else:
            raise SystemExit("ERROR: Unsupported distribution " + source["name"] + " - please check your images-sources.yaml")
        if catalog_update:
            print("Update found for " + source["name"] + " " + release["name"])
            print("New release " + catalog_update["version"])
            # catalog_update anreichern mit _allen_ Daten für die DB
            catalog_update["name"] = source["name"] + " " + release["name"]
            catalog_update["distribution_name"] = source["name"]
            catalog_update["distribution_release"] = release["name"]
            catalog_update["release"] = release["name"]

            write_or_update_catalog_entry(connection, catalog_update)
            updated_releases.append(release["name"])
        else:
            print("No update found for " + source["name"] + " " + release["name"])

    return updated_releases
