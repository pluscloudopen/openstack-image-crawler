import yaml

from loguru import logger
from pathlib import Path


def config_read(name, msg="config"):
    path = Path(name)
    if not path.is_file():
        return None

    try:
        config = yaml.safe_load(Path(name).read_text())
    except PermissionError:
        logger.error("could not open config - please check file permissions")
        return None
    except yaml.YAMLError as error:
        logger.error(error)
        return None

    logger.info("Successfully read %s from %s" % (msg, name))

    return config
