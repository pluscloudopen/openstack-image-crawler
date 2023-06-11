# fedora.py
#
# crawl distribution Fedora Linux

import requests
import re

from crawler.web.generic import url_get_last_modified, url_fetch_content

from bs4 import BeautifulSoup
from loguru import logger


def get_latest_release(release):
    # as specified in image-sources.yaml
    # baseURL: https://ftp.plusline.net/fedora/linux/releases/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]
    release_pattern = re.compile(r"(\d+)")
    releases_path = base_url + "/" + release["releasepath"]

    request = requests.get(releases_path, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    last_link = ""

    # we need the last link matching release_pattern
    for link in soup.find_all("a"):
        data = link.get("href")

        if release_pattern.search(data):
            last_link = data

    # last_link contains "38/" relative link address with ending slash
    extract = release_pattern.search(last_link)
    release_id = extract.group(0)

    logger.debug("release_id: " + release_id)

    # ToDo - in case of no last_link found we need an None
    return release_id

def get_image_filename(release, images_url):
    request = requests.get(images_url, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    last_link = ""

    for link in soup.find_all("a"):
        data = link.get("href")

        if release["extension"] in data:
            # logger.debug("match: " + data)
            last_link = data

    if len(last_link) > 0:
        return last_link
    else:
        return None

def get_checksum(release, images_url, image_filename):
    request = requests.get(images_url, allow_redirects=True)
    soup = BeautifulSoup(request.text, "html.parser")

    last_link = ""

    # we need the last link matching CHECKSUM
    for link in soup.find_all("a"):
        data = link.get("href")

        if release["checksumname"] in data:
            last_link = data

    logger.debug("last_link: " + last_link)

    checksum_url = images_url + "/" + last_link

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

def fedora_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://ftp.plusline.net/fedora/linux/releases/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    release_id = get_latest_release(release)

    images_url = base_url + release["releasepath"] + "/" + release_id + "/" + release["imagepath"]

    image_filename = get_image_filename(release, images_url)

    if image_filename is None:
        logger.warn("did not find any matching filenames")
        return None

    logger.debug("image_filename: " +  image_filename)

    logger.debug("checksum_path: " + images_url)

    current_checksum = get_checksum(release, images_url, image_filename)

    if current_checksum is None:
        logger.error(
            "no matching checksum found - check image (%s) "
            "and checksum filename (%s)" % (image_filename, release["checksumname"])
        )
        return None

    logger.debug("current_checksum: " + current_checksum)

    # as specified in image-sources.yaml
    # algorithm: sha256
    current_checksum = release["algorithm"] + ":" + current_checksum

    if current_checksum != last_checksum:
        logger.debug("current_checksum " + current_checksum + " differs from last_checksum " + last_checksum)

        image_url = images_url + "/" + image_filename

        logger.debug("image_url: " + image_url)

        image_filedate = url_get_last_modified(image_url)

        logger.debug("image_filedate: " + image_filedate)

        update = {}
        update["release_date"] = image_filedate
        update["url"] = image_url
        update["version"] = image_filedate.replace("-", "")
        update["checksum"] = current_checksum
        update["release_id"] = release_id

        return update

    return None
