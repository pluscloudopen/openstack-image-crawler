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

Tested on Ubuntu 20.04 LTS + 22.04 LTS (should work with Python 3.8+)

```
sudo apt install git python3-pip python3-venv
git clone git@github.com:costelter/openstack-image-crawler.git
cd openstack-image-crawler
python3 -m venv $HOME/.oic
source $HOME/.oic/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
./image-crawler.py --init-db
```

or use the little setup.sh script

```
git clone git@github.com:costelter/openstack-image-crawler.git
cd openstack-image-crawler
./setup.sh
```

## Requirements

Git Repositoy for the generated image yaml files. Access currently only via SSH (+key) supported.

```
remote_repository: "git@git.coolcompany.com:openstack/image-catalogs.git"
```
(in etc/config.yaml)

If there is no remote_repository entry in the config, the git actions are disabled. In the example config.yaml the entry is named no_remote_repository and therefore disabled. Just remove the "no_" and enter your repository URL. Keep in mind that you will have to enable repository access via ssh key and the right ssh key for the user calling the git command.

## Changes

- in etc/config.yaml exports: is now **local_repository**
- renamed openstack-image-crawler to image-crawler
- added git support

ToDo:

- build container, docker-compose file
- explain workflow
- explain structure of config.yaml, image-sources.yaml
- improve error handling
