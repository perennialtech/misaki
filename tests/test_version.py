import importlib.metadata

import misaki


def test_package_version_consistency():
    pkg_ver = importlib.metadata.version("misaki")
    assert misaki.__version__ == pkg_ver
