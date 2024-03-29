# OpenStack Image Crawler

## Background

The Image Crawler originated at [plusserver GmbH](https://plusserver.com) due to the demand for automated regular updates of OpenStack images. With the release of the Image Manager by [OSISM GmbH](https://osism.tech) we already had a tool for uploading and managing all used images as defined in its [catalog files](https://docs.osism.tech/openstack-image-manager/configuration.html).

And this is where Image Crawler comes into play. The Image Crawler is able to generate these catalog files with the data crawled and stored in its database. The templates in the templates directory are used to generate files needed by the Image Manager.

You are not bound to use it with the Image Crawler (although we recommend it). The templates are [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templates. So the output generated by the Image Crawler is only limited by the capabilities of [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) and the data crawled and stored by the Image Crawler.

You could use the templates to generate all necessary commands for the openstack cli to upload the images directly for example.

## How does it work?

The Image Crawler reads the release information from image-sources.yaml to build the URL for the checksum file of the latest release of a version and grabs the checksum for the filename as defined in the image-sources.yaml.

So for example in case of Ubuntu 20.04 the Image Crawler would download the URL:

https://cloud-images.ubuntu.com/releases/focal/release/SHA256SUMS

and grab the checksum for the file **ubuntu-20.04-server-cloudimg-amd64.img**

```
[..]
24673aa86785573d3a92e15166ff81beff88cbb0abc01938f156eb1332e87cd3 *ubuntu-20.04-server-cloudimg-s390x.img
2674f031d8b29a90bbbb2e635bbbca73e43c9c1e3490b1ee4d56f2dedaef9e7c *ubuntu-20.04-server-cloudimg-s390x.tar.gz
2b89f36eb81cb3bbcdfbc0f6dc3f2b624d3fa861ce5d8b5c5eeea7e8b8ad9b0d *ubuntu-20.04-server-cloudimg-amd64-disk-kvm.manifest
3895e38566e5c2c019f5c6f825ab7570ee34dac6b9142fab0c7e5a78084c4280 *ubuntu-20.04-server-cloudimg-amd64.img
38cdaac4d3efe604360bbaafce183463705583b963103b69b41ef156ae12d19d *ubuntu-20.04-server-cloudimg-amd64.ova
434d124ec8c855ff7d754993106f4d60231ec35ddf7fde52b1f7538982dd2556 *ubuntu-20.04-server-cloudimg-ppc64el.manifest
[..]
```
(excerpt of an SHA256SUMS file)

When the Image Crawler runs for the first time it would just download all other information needed for creating the catalog file(s) for the Image Manager. At all subsequent runs it would compare the last known checksum for the image with the current checksum found in the directory of the latest release. If the checksum differs, it would download all other new information needed.

These additional informations are the release date (1), the complete url (2) for this specific version, the name of the version (3) as it is used in the catalog file for the Image Manager.

In our example for Ubuntu 20.04 these would be:

1. 2023-01-07
2. https://cloud-images.ubuntu.com/releases/focal/release-20230107/ubuntu-20.04-server-cloudimg-amd64.img
3. 20230107

As you can see the release version (20230107) is part of the URL in which the release version is stored and under which it can be found even if there is already a newer release. This is makes it easier if you want to spawn a new openstack region with the same images as in your existing regions.

Debian has a simliar way to offer its images for download.

But there are many other OS distributions and all have their own way of offering their images. OpenSUSE and Almalinux for example only offer the latest image of a release.

So for addition of other images it will be necessary to extend the Image Crawler.
