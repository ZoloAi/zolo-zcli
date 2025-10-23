# zCLI/version.py — Version Management
# ───────────────────────────────────────────────────────────────
"""Version management for zCLI package."""

__version__ = "1.5.4"
__version_info__ = (1, 5, 4)

# Package metadata
__name__ = "zolo-zcli"
__description__ = "A YAML-driven CLI framework for interactive applications"
__author__ = "Gal Nachshon"
__author_email__ = "gal@zolo.media"

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get the version as a tuple."""
    return __version_info__

def get_package_info():
    """Get complete package information."""
    return {
        "name": __name__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "author_email": __author_email__,
        "version_info": __version_info__
    }

