from pbr import version as pbr_version

# RALLY_VENDOR = "RedHat"
# RALLY_PRODUCT = "Eventool"
# RALLY_PACKAGE = None  # OS distro package version suffix

loaded = False
version_info = pbr_version.VersionInfo("eventool")


def version_string():
    return version_info.version_string()
