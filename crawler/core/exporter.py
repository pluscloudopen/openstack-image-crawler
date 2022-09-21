from jinja2 import Template

from crawler.core.database import read_release_from_catalog


def export_image_catalog(connection, sources_catalog, local_repository):
    for source in sources_catalog['sources']:
        distribution = source['name']
        print("Exporting image catalog for " + distribution)
        header_file = open("templates/header.yaml")
        catalog_export = header_file.read()
        header_file.close()

        image_template_filename = "templates/" + distribution.lower().replace(" ", "_") + ".yaml.j2"
        image_template_file = open(image_template_filename, "r")
        image_template = Template(image_template_file.read())
        image_template_file.close()

        for release in source['releases']:
            # prüfen, ob catalog leer !!
            release_catalog = read_release_from_catalog(connection, distribution, release['name'])
            release_catalog['name'] = distribution
            release_catalog['os_distro'] = distribution.lower()
            release_catalog['os_version'] = release['name']

            catalog_export = catalog_export + image_template.render(catalog=release_catalog) + "\n"

        # print(catalog_export)

        image_catalog_export_filename = local_repository + "/" + distribution.lower().replace(" ", "_") + ".yaml"
        image_catalog_export_file = open(image_catalog_export_filename, "w")
        image_catalog_export_file.write(catalog_export)
        image_catalog_export_file.close()

    # error handling !!
    # return None
