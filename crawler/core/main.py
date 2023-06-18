from crawler.updater.service import image_update_service, image_crawl_back_service
from loguru import logger


def crawl_back_image_sources(image_source_catalog, database):

    updated_sources = {}
    for source in image_source_catalog["sources"]:
        logger.info("Checking updates for Distribution " + source["name"])
        updated_releases = image_crawl_back_service(database, source)
        if updated_releases:
            updated_sources[source["name"]] = {}
            updated_sources[source["name"]]["releases"] = updated_releases

    return updated_sources

def crawl_image_sources(image_source_catalog, database):

    updated_sources = {}
    for source in image_source_catalog["sources"]:
        logger.info("Checking updates for Distribution " + source["name"])
        updated_releases = image_update_service(database, source)
        if updated_releases:
            updated_sources[source["name"]] = {}
            updated_sources[source["name"]]["releases"] = updated_releases

    return updated_sources
