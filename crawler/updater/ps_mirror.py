# ps_mirror.py
#
# crawl mirror.plusserver.com for plusserver made images

from crawler.web.generic import url_get_last_modified
from crawler.web.directory import web_get_checksum

from loguru import logger


def ps_mirror_update_check(release, last_checksum):
    # as specified in image-sources.yaml
    # baseURL: https://mirror.plusserver.com/images/os/
    if not release["baseURL"].endswith("/"):
        base_url = release["baseURL"] + "/"
    else:
        base_url = release["baseURL"]

    checksum_url = base_url + release["checksumname"]

    logger.debug("checksum_url: " + checksum_url)

    # as specified in image-sources.yaml
    # imagename: ubuntu-22.04
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
        image_url = base_url + imagename

        logger.debug("image_url:" + image_url)

        image_filedate = url_get_last_modified(image_url)

        logger.debug("image_filedate:" + image_filedate)

        update = {}
        update["release_date"] = image_filedate
        update["url"] = image_url
        update["version"] = image_filedate.replace("-", "")
        update["checksum"] = current_checksum
        return update

    return None
