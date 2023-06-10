# alma.py
#
# crawl distribution Alma Linux

import requests
import datetime

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum, web_get_current_image_metadata

from bs4 import BeautifulSoup
from loguru import logger


def build_image_url(release, versionpath):
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    # if not versionpath.endswith("/"):
    #    versionpath = versionpath + "/"

    return (
        base_url + release["releasepath"] + "/" + versionpath
    )

def release_date_from_version(release_version):
    # 20230606
    release_date = (
        release_version[0:4]
        + "-"
        + release_version[4:6]
        + "-"
        + release_version[6:8]
    )
    return release_date

def version_from_path(versionpath):
    # the path within the releases directory has the format
    #    release-20230606/
    # or even in some cases
    #    release-20221101.1/

    if versionpath.endswith("/"):
        versionpath = versionpath.rstrip("/")
    # if the path ends with an .X extension, strip it
    if versionpath.find(".") != -1:
        parts = versionpath.split(".")
        versionpath = parts[0]

    # and remove the "release-" in front of the version
    return versionpath.replace("release-", "")

def get_metadata(release, image_filedate):
    filedate = image_filedate.replace("-", "")
    requestURL = release["baseURL"]

    request = requests.get(requestURL, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    for link in soup.find_all("a"):
        data = link.get("href")
        if data.find(filedate) != -1:
            release_version_path = data
            version = version_from_path(release_version_path)
            if version is None:
                return None

            release_date = release_date_from_version(version)
            if release_date is None:
                return None

            logger.debug("url: " + build_image_url(release, release_version_path))
            logger.debug("last version: " + version)
            logger.debug("release_date: " + release_date)

            return {
                "url": build_image_url(
                    release, release_version_path
                ),
                "version": version,
                "release_date": release_date,
            }

    # release is behind file date
    search_date = datetime.date(int(filedate[0:4]), int(filedate[4:6]), int(filedate[6:8]))

    max_days_back = 6
    days_back = 1

    while days_back <= max_days_back:
        search_date = search_date - datetime.timedelta(days=1)
        version = search_date.strftime("%Y%m%d")

        for link in soup.find_all("a"):
            data = link.get("href")
            if data.find(version) != -1:
                release_version_path = data
                version = version_from_path(release_version_path)
                if version is None:
                    return None

                release_date = release_date_from_version(version)
                if release_date is None:
                    return None

                return {
                    "url": build_image_url(
                        release, release_version_path
                    ),
                    "version": version,
                    "release_date": release_date,
                }

        days_back = days_back + 1

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

    logger.debug("current_checksum: " + current_checksum)

    if current_checksum is None:
        logger.error(
            "no matching checksum found - check image (%s) "
            "and checksum filename (%s)" % (imagename, release["checksumname"])
        )
        return None

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
