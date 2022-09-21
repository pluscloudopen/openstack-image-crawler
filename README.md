# OpenStack Image Crawler

OpenStack Image Crawler for checking image sources, gathering update information and generating image catalog files for the OpenStack Image Manager (or similiar tools)

## Getting started

Usage:

```
./image-crawler.py -h

plusserver Image Crawler v0.1

usage: oic.py [-h] [--config CONFIG] [--sources SOURCES] [--init-db] [--export-only] [--updates-only]

checks cloud image repositories for new updates and keeps track of all images within its sqlite3 database

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    specify the config file to be used (default: etc/config.yaml)
  --sources SOURCES  specify the sources file to be used - overrides value from config file
  --init-db          initialize image catalog database
  --export-only      export only existing image catalog
  --updates-only     check only for updates, do not export catalog
```

## Installation

Tested on Ubuntu 20.04 LTS (should work with Python 3.8+)

```
git git@git.ps-intern.de:openstack/openstack-image-crawler.git
sudo apt install python3-venv
cd openstack-image-crawler
python3 -m venv .oic
source .oic/bin/activate
pip install wheel validators requests pyyaml bs4 jinja2
./image-crawler.py --init-db
```

## Requirements

Git Repositoy for the generated image yaml files. Access currently only via SSH (+key) supported.

```
remote_repository: "git@git.gadgetlab.de:openstack/image-catalogs.git"
```
(in etc/config.yaml)

if not set, it will not handle the git repos part for you (untested).


## Changes

- in etc/config.yaml exports: is now **local_repository**
- renamed openstack-image-crawler to image-crawler
- added git support

ToDo:

- create requirements.txt
- build container, docker-compose file
- explain workflow
- explain structure of config.yaml, image-sources.yaml
- improve error handling
