# rocky.py
#
# crawl distribution Rocky Linux

import requests
import re

from crawler.web.generic import url_get_last_modified, url_fetch_content
from crawler.web.directory import web_get_current_image_metadata

from bs4 import BeautifulSoup
from loguru import logger


def build_image_url(release, major_minor, imagefile_name):
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/" + major_minor + "/"
    else:
        base_url = release["baseURL"] + major_minor + "/"

    # if not versionpath.endswith("/"):
    #    versionpath = versionpath + "/"

    return (
        base_url + release["imagepath"] + "/" + imagefile_name
    )

def get_metadata(release):
    # as specified in image-sources.yaml
    # baseURL: https://download.rockylinux.org/pub/rocky/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/" + release["name"] + "/"
    else:
        base_url = release["baseURL"] + release["name"] + "/"

    requestURL = base_url + release["imagepath"]
    # TODO: make this configurable in image-source.yaml
    #
    #       group(1) contains major version as 9
    #       group(2) contains full version with minor version number as 9.2
    #       group(3) contains release date as 20230513
    #       group(4) contains release date suffix 0 (subversion?)
    #       ex. Rocky-9-GenericCloud-Base-9.2-20230513.0.x86_64.qcow2

    filename_pattern = re.compile(r"Rocky-(\d+)-GenericCloud-Base-(\d+\.\d+)-(\d+).(\d+)\.x86_64\.qcow2")

    logger.debug("request_URL: " + requestURL)

    request = requests.get(requestURL, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    for link in soup.find_all("a"):
        data = link.get("href")
        # logger.debug("data: " + data)

        if filename_pattern.search(data):
            logger.debug("pattern matched for " + data)
            extract = filename_pattern.search(data)
            major_minor = extract.group(2)
            version = extract.group(3)

            release_date = (
                version[0:4]
                + "-"
                + version[4:6]
                + "-"
                + version[6:8]
            )
            logger.debug("url: " + build_image_url(release, major_minor, data))
            logger.debug("last version: " + version)
            logger.debug("release_date: " + release_date)

            return {
                "url": build_image_url(release, major_minor, data),
                "version": version,
                "release_date": release_date,
            }

    return None

def get_checksum(checksum_url, image_filename):

    checksum_list = url_fetch_content(checksum_url)
    if checksum_list is None:
        return None

    for line in checksum_list.splitlines():
        # logger.debug("line: " + line)

        # skip comment starting with hash
        if re.match('^#', line):
            continue
        if image_filename in line:
            # logger.debug("matched: " + line)
            (filename, new_checksum) = line.split(" = ")
            # logger.debug("new_checksum: " + new_checksum)

            return new_checksum

    return None

def rocky_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://download.rockylinux.org/pub/rocky/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/" + release["name"] + "/"
    else:
        base_url = release["baseURL"] + release["name"] + "/"

    checksum_url = base_url + release["imagepath"] + "/" + release["checksumname"]

    logger.debug("checksum_url: " + checksum_url)

    # as specified in image-sources.yaml
    # imagename: Rocky-9-GenericCloud.latest.x86_64
    # extension: qcow2
    imagename = release["imagename"] + "." + release["extension"]

    logger.debug("imagename: " + imagename)

    current_checksum = get_checksum(checksum_url, imagename)

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

        image_metadata = get_metadata(release)
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
