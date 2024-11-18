# flatcar.py
#
# crawl distribution Flatcar Container Linux

import requests
import re

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum

from bs4 import BeautifulSoup
from loguru import logger


def build_image_url(release, versionpath):
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    if not versionpath.endswith("/"):
        versionpath = versionpath + "/"

    return (
        base_url + versionpath + release["imagename"] + "." + release["extension"]
    )

def get_metadata(release, image_filedate):
    filedate = image_filedate.replace("-", "")
    requestURL = release["baseURL"]
    # version format is 3510.2.2
    version_pattern = re.compile(r"\d+\.\d+\.\d+")

    request = requests.get(requestURL, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    last_link = ""

    # we need the last link matching version_pattern
    for link in soup.find_all("a"):
        data = link.get("href")

        if version_pattern.search(data):
            last_link = data

    # last_link contains "./3510.2.2/" relative link address with dot and slashes
    extract = version_pattern.search(last_link)
    version = extract.group(0)

    logger.debug("url: " + build_image_url(release, version))
    logger.debug("last version: " + version)
    logger.debug("release_date: " + filedate)

    return {
        "url": build_image_url(release, version),
        "version": version,
        "release_date": image_filedate,
    }

def flatcar_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://cloud-images.flatcar.com/releases/jammy/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    checksum_url = base_url + release["releasepath"] + "/" + release["checksumname"]

    logger.debug("checksum_url: " + checksum_url)

    # as specified in image-sources.yaml
    # imagename: flatcar-22.04-server-cloudimg-amd64
    # extension: img
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

        logger.debug("image_url: " + image_url)

        image_filedate = url_get_last_modified(image_url)

        logger.debug("image_filedate: " + image_filedate)

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
