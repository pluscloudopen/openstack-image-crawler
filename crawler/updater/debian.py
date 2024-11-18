# debian.py
#
# crawl distribution Debian

import requests
import datetime
import re

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum, web_get_current_image_metadata

from bs4 import BeautifulSoup
from loguru import logger

from pprint import pprint

def build_image_url(release, versionpath):
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    if not versionpath.endswith("/"):
        versionpath = versionpath + "/"

    return (
        base_url
        + versionpath
        + release["imagename"]
        + "-"
        + version_from_path(versionpath)
        + "."
        + release["extension"]
    )

def release_date_from_version(release_version):
    # 20230601-1398
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
    #    20230601-1398/

    if versionpath.endswith("/"):
        versionpath = versionpath.rstrip("/")

    return versionpath

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

        days_back = days_back + 1

    return None

def debian_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://cloud.debian.org/images/cloud/bullseye/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    checksum_url = base_url + release["releasepath"] + "/" + release["checksumname"]

    logger.debug("checksum_url: " + checksum_url)

    # as specified in image-sources.yaml
    # imagename: debian-11-genericcloud-amd64
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
    # algorithm: sha512
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

def debian_crawl_release(release):
    version_dir_list = []
    updates_list = []

    # as specified in image-sources.yaml
    # baseURL: https://cloud.debian.org/images/cloud/bullseye/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    # make it configurable?
    release_pattern = re.compile(r"(\d+)-(\d+)")
    releases_path = base_url

    logger.info("Looking for release versions at: " + releases_path)

    request = requests.get(releases_path, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    last_link = ""

    # we need the last link matching release_pattern
    for link in soup.find_all("a"):
        data = link.get("href")

        if release_pattern.search(data):
            # debian directory listing contains the link twice
            # one href for the folder icon
            # one href for the directory name
            # so prevent duplicates
            if last_link != data:
                last_link = data
                version_dir_list.append(last_link)
                # logger.debug("matching entry: " + last_link)

    # number of entries to crawl back as defined in image-sources.yaml
    # via limit - can be set per release
    if "limit" in release:
        limit = release["limit"]
    else:
        limit = 3

    for version_path in version_dir_list[-limit:]:
        extract = release_pattern.search(version_path)

        # version_path contains "20230612-1409" release version
        version = version_from_path(version_path)

        logger.debug("Version to work on: " + version)

        # as specified in image-sources.yaml
        # imagename: debian-11-genericcloud-amd64
        # extension: qcow2
        imagename = release["imagename"] + "-" + version  + "." + release["extension"]

        checksum_url = base_url + version_path + release["checksumname"]
        logger.debug("checksum_url: " + checksum_url)
        version_checksum = web_get_checksum(checksum_url, imagename)
        logger.debug("checksum: " + version_checksum)
        version_checksum = release["algorithm"] + version_checksum

        logger.debug("checksum_url: " + version_checksum)

        release_date = release_date_from_version(version)

        logger.debug("release_date: " + release_date)

        url = build_image_url(release, version_path)

        logger.debug("url: " + url)

        version_entry = {}
        version_entry["release_date"] = release_date
        version_entry["url"] = url
        version_entry["version"] = version
        version_entry["checksum"] = version_checksum

        updates_list.append(version_entry)

    return updates_list
