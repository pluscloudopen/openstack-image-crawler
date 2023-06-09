# ubuntu.py
#
# crawl distribution Flatcar Container Linux

import requests
import re

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum

from bs4 import BeautifulSoup
from pprint import pprint

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
            # print("flatcat.py/get_metadata data matched: " + data)
            last_link = data

    # last_link contains "./3510.2.2/" relative link address with dot and slashes
    extract = version_pattern.search(last_link)
    pprint(extract)
    version = extract.group(0)

    # print("last version: " + version)

    # print("image_url:" + build_image_url(release, version))

    return {
        "url": build_image_url(release, version),
        "version": version,
        "release_date": filedate,
    }

def flatcar_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://cloud-images.flatcar.com/releases/jammy/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    checksum_url = base_url + release["releasepath"] + "/" + release["checksumname"]

    print("flatcar_update_check/checksum_url:" + checksum_url)

    # as specified in image-sources.yaml
    # imagename: flatcar-22.04-server-cloudimg-amd64
    # extension: img
    imagename = release["imagename"] + "." + release["extension"]

    print("flatcar_update_check/imagename:" + imagename)

    current_checksum = web_get_checksum(checksum_url, imagename)

    print("flatcar_update_check/current_checksum:" + current_checksum)

    if current_checksum is None:
        print(
            "ERROR: no matching checksum found - check image (%s) "
            "and checksum filename (%s)" % (imagename, release["checksumname"])
        )
        return None

    # as specified in image-sources.yaml
    # algorithm: sha256
    current_checksum = release["algorithm"] + ":" + current_checksum

    if current_checksum != last_checksum:
        print("DO something")
        image_url = base_url + release["releasepath"] + "/" + imagename

        print("flatcar_update_check/image_url:" + image_url)

        image_filedate = url_get_last_modified(image_url)

        print("flatcar_update_check/image_filedate:" + image_filedate)

        image_metadata = get_metadata(release, image_filedate)
        if image_metadata is not None:
            pprint(image_metadata)
            update = {}
            update["release_date"] = image_metadata["release_date"]
            update["url"] = image_metadata["url"]
            update["version"] = image_metadata["version"]
            update["checksum"] = current_checksum
            return update
        else:
            return None

    return None
