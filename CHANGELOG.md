# Changelog

## 2023-06-XX

- reverted historian.py to last known working version, added notification for unsupported distributions
- improved exporter - now warns when there is no release data in database
- added loguru to git/base.py
- changed logging
- improved git error handling
- improved database handling for releases with "all" as introduced with Fedora
- fixed Flatcar release_date entry
- added new crawl-back-eval.py as seperate script for evalution
- crawl-back-eval.py will be integrated into image-crawler.py and historian.py hack will be removed
- crawl back support for Debian, Ubuntu and Fedora added

## 2023-06-11
- refactoring of updater parts - split into single files for each distribution
- removed generic release_update_check from updater/service.py
- added support Flatcar Container Linux
- updated README.md
- added loguru for easy configuration of logging
- added optional debug output (via loglevel)
- added --debug as argument
- added first try on Fedora Linux Support to crawler
- added Debian Linux 12 aka bookworm to sample image-sources.yaml
- added Rocky Linux

## 2023-06-01
- updated example Dockerfile to new repos

## 2023-05-30

- fix Alma Linux URL generation which suffered from the last Ubuntu fix
- added the ability to limit the number of versions per release (default 3 - if not set via "limit: X")
- removed Ubuntu 18.04 LTS due to reaching EOL in sample image-sources.yaml

## 2023-05-24

- added version tag
- docker example added for use in a pipeline
- improved git handling
- added more documentation
- moved from openstack-image-manager back to its own repo

## 2023-01-09

- added more documentation on usage and functionality

## 2023-01-05

- added ssh_git_command for git (costelter)
- added branch support (costelter)
- fixed output of export path informational (costelter)

## 2023-01-02

- fixed static path for templates (costelter)
