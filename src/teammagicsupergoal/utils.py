import pkg_resources as __pkg_resources


def __get_resource_path(package_or_requirement, resource_name):
    return __pkg_resources.normalize_path(
        __pkg_resources.resource_filename(
            package_or_requirement, resource_name))


def get_data_path(filename):
    return __get_resource_path(__name__, 'data/' + filename)
