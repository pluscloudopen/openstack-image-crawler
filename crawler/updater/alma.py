# alma.py
#
# crawl distribution Alma Linux

import requests
import re

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum, web_get_current_image_metadata

from bs4 import BeautifulSoup
from loguru import logger


def build_image_url(release, imagefile_name):
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    # if not versionpath.endswith("/"):
    #    versionpath = versionpath + "/"

    return (
        base_url + release["releasepath"] + "/" + imagefile_name
    )

def get_metadata(release, image_filedate):
    filedate = image_filedate.replace("-", "")
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    requestURL = release["baseURL"] + release["releasepath"]
    # TODO: make this configurable in image-source.yaml
    #
    #       group(1) contains major version as 9
    #       group(2) contains full version with minor version number as 9.2
    #       group(3) contains release date as 20230513
    #       ex. AlmaLinux-9-GenericCloud-9.2-20230513.x86_64.qcow2

    filename_pattern = re.compile(r"AlmaLinux-(\d+)-GenericCloud-(\d+.\d+)-(\d+).x86_64")

    logger.debug("request_URL: " + requestURL)

    request = requests.get(requestURL, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    for link in soup.find_all("a"):
        data = link.get("href")
        logger.debug("data: " + data)

        if filename_pattern.search(data):
            logger.debug("pattern matched for " + data)
            extract = filename_pattern.search(data)
            release_date = extract.group(3)
            version = release_date

            logger.debug("url: " + build_image_url(release, data))
            logger.debug("last version: " + version)
            logger.debug("release_date: " + image_filedate)

            return {
                "url": build_image_url(release, data),
                "version": version,
                "release_date": image_filedate,
            }

    return None

def alma_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://repo.almalinux.org/almalinux/9/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    checksum_url = base_url + release["releasepath"] + "/" + release["checksumname"]

    logger.debug("checksum_url: " + checksum_url)

    # as specified in image-sources.yaml
    # imagename: AlmaLinux-9-GenericCloud-latest.x86_64
    # extension: qcow2
    imagename = release["imagename"] + "." + release["extension"]

    logger.debug("imagename: " + imagename)

    current_checksum = web_get_checksum(checksum_url, imagename)

    if current_checksum is None:
        logger.error(
            "no matching checksum found - check image (%s) "
            "and checksum filename (%s)" % (imagename, release["checksumname"])
        )
        return None

    logger.debug("current_checksum: " + current_checksum)

    # as specified in image-sources.yaml
    # algorithm: sha256
    current_checksum = release["algorithm"] + ":" + current_checksum

    if current_checksum != last_checksum:
        logger.debug("current_checksum " + current_checksum + " differs from last_checksum " + last_checksum)
        image_url = base_url + release["releasepath"] + "/" + imagename

        logger.debug("image_url:" + image_url)

        image_filedate = url_get_last_modified(image_url)

        logger.debug("image_filedate:" + image_filedate)

        image_metadata = get_metadata(release, image_filedate)
        if image_metadata is not None:
            logger.debug("got metadata")
            update = {}
            update["release_date"] = image_metadata["release_date"]
            update["url"] = image_metadata["url"]
            update["version"] = image_metadata["version"]
            update["checksum"] = current_checksum
            return update
        else:
            logger.warning("got no metadata")
            return None

    return None
