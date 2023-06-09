# OpenStack Image Crawler

OpenStack Image Crawler for checking image sources, gathering update information and generating image catalog files for the [OpenStack Image Manager](https://github.com/osism/openstack-image-manager) (or similiar tools).

Supported distributions:

- Ubuntu Linux
- Debian Linux
- AlmaLinux
- Flatcar Container Linux

Note: Flatcar Container Linux offers only zipped images, so a direct upload via OpenStack Image Manager/Glance is not supported (yet).

## Requirements
### Git repository for holding the image catalogs (optional)

If you want to use the builtin git repository handling for storing the image catalog exports, you need to create a repository before running the image crawler the first time. Alternatively you have to remove the "repository" directory and run it again.

Currently only access via SSH (key) is supported. The image crawler will checkout the "main" (default) branch of your git repository.

If there is no remote_repository entry in the config, the git actions are disabled. In the example config.yaml the entry is named no_remote_repository and therefore disabled. Just remove the "no_" and enter your repository URL. Keep in mind that you will have to enable repository access via ssh key and the right ssh key for the user calling the git command.

## Installation

Tested on Ubuntu 20.04 LTS + 22.04 LTS. Should work with Python 3.8+ on other OSs, too. Optional: build the docker container.

```
sudo apt install git python3-pip python3-venv
git clone git@github.com:costelter/openstack-image-crawler.git
cd openstack-image-crawler
python3 -m venv .oic
source .oic/bin/activate
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

## Getting started

### Image Crawler

Usage:

```
./image-crawler.py -h

plusserver Image Crawler v4.0

usage: image-crawler.py [-h] [--config CONFIG] [--sources SOURCES] [--init-db] [--export-only] [--updates-only]

checks cloud image repositories for new updates and keeps track of all images within its sqlite3 database

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    specify the config file to be used (default: etc/config.yaml)
  --sources SOURCES  specify the sources file to be used - overrides value from config file
  --init-db          initialize image catalog database
  --export-only      export only existing image catalog
  --updates-only     check only for updates, do not export catalog
```

### Helper: Historian

./historian.py

Crawls the complete cloud web directories (for Ubuntu and Debian only) and gathers their metadata. Some old versions have not all necessary metadata and will be skipped.

**WARNING!** historian.py is meant to be run on an empty image-catalog.db only. Create an empty database with image-crawler first.

```
./image-crawler.py --init-db
./historian.py
```

As time permits the mechanismus relying on last entry = last version (and therefore last checksum) will be improved. This will be someday integrated into the image-crawler as soon as it is smarter. Planned features: specifying a time range or number of historic releases.
