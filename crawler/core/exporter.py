from jinja2 import Template
import os

from crawler.core.database import read_release_from_catalog
from loguru import logger

from pprint import pprint

def export_image_catalog(
    connection, sources_catalog, updated_sources, local_repository, template_path
):
    # "smart" export - only releases with updates will be written
    # create directory (once) - only necessary when not created by git clone
    if not os.path.exists(local_repository):
        try:
            logger.info("Creating repository directory (%s)" %
                        local_repository)
            os.makedirs(local_repository)
        except os.error as error:
            logger.error(
                "Creating directory %s failed with %s"
                % (local_repository, error)
            )
            raise SystemExit(1)

    for source in sources_catalog["sources"]:
        if source["name"] in updated_sources:
            distribution = source["name"]
            logger.info("Exporting image catalog for " + distribution)

            catalog_export = ""

            image_template_filename = (
                template_path +
                "/" +
                distribution.lower().replace(" ", "_") +
                ".yml.j2"
            )
            image_template_file = open(image_template_filename, "r")
            image_template = Template(image_template_file.read())
            image_template_file.close()

            for release in source["releases"]:
                #normalize base url again
                if not release["baseURL"].endswith("/"):
                    release["baseURL"] = release["baseURL"] + "/"

                if "limit" in release:
                    limit = release["limit"]
                else:
                    limit = 3

                release_catalog = read_release_from_catalog(
                    connection, distribution, release["name"], limit
                )
                if release_catalog["versions"]:
                    release_catalog["name"] = distribution
                    release_catalog["os_distro"] = distribution.lower()
                    release_catalog["os_version"] = release["name"]
                    release_catalog["codename"] = release["codename"]
                    logger.debug("Rendering template for " +
                                 release_catalog["name"] + " " +
                                 release_catalog["os_version"])

                    catalog_export = (
                        catalog_export
                        + image_template.render(catalog=release_catalog,
                                                metadata=release)
                        + "\n"
                    )
                else:
                    logger.warning("got no catalog entries for " +
                                   distribution + " " +
                                   release["name"])

            if len(release_catalog) > 0:
                header_file = open(template_path + "/header.yml")
                catalog_header = header_file.read()
                header_file.close()

                catalog_export = catalog_header + catalog_export

                image_catalog_export_filename = (
                    local_repository + "/" +
                    distribution.lower().replace(" ", "_") + ".yml"
                )
                image_catalog_export_file = open(
                    image_catalog_export_filename, "w"
                    )
                image_catalog_export_file.write(catalog_export)
                image_catalog_export_file.close()
            else:
                logger.debug("nothing to export for " + distribution)


def export_image_catalog_all(
    connection, sources_catalog, local_repository, template_path
):
    # export all releases - used with --export-only
    # create directory (once) - only necessary when not created by git clone
    if not os.path.exists(local_repository):
        try:
            logger.info("Creating repository directory (%s)" %
                        local_repository)
            os.makedirs(local_repository)
        except os.error as error:
            logger.error(
                "Creating directory %s failed with %s"
                % (local_repository, error)
            )
            raise SystemExit(1)

    for source in sources_catalog["sources"]:
        distribution = source["name"]
        logger.info("Exporting image catalog for " + distribution)

        catalog_export = ""

        image_template_filename = (
            template_path + "/" +
            distribution.lower().replace(" ", "_") + ".yml.j2"
        )
        image_template_file = open(image_template_filename, "r")
        image_template = Template(image_template_file.read())
        image_template_file.close()

        for release in source["releases"]:
            if "limit" in release:
                limit = release["limit"]
            else:
                limit = 3

            release_catalog = read_release_from_catalog(
                connection, distribution, release["name"], limit
            )
            if release_catalog["versions"]:
                release_catalog["name"] = distribution
                release_catalog["os_distro"] = distribution.lower()
                release_catalog["os_version"] = release["name"]
                release_catalog["codename"] = release["codename"]
                logger.debug("Rendering template for " +
                             release_catalog["name"] + " " +
                             release_catalog["os_version"])

                catalog_export = (
                    catalog_export
                    + image_template.render(catalog=release_catalog,
                                            metadata=release)
                    + "\n"
                )

            else:
                logger.warning("got no catalog entries for " +
                               distribution + " " + release["name"])

        if len(catalog_export) > 0:
            image_catalog_export_filename = (
                            local_repository + "/" +
                            distribution.lower().replace(" ", "_") +
                            ".yml"
                        )

            header_file = open(template_path + "/header.yml")
            catalog_header = header_file.read()
            header_file.close()

            catalog_export = catalog_header + catalog_export

            logger.debug("Writing catalog file for " + distribution)
            image_catalog_export_file = open(image_catalog_export_filename, "w")
            image_catalog_export_file.write(catalog_export)
            image_catalog_export_file.close()
        else:
            logger.debug("nothing to export for " + distribution)
