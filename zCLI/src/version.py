# zKernel/version.py — Version Management
# ───────────────────────────────────────────────────────────────
"""Version management for zKernel package."""

__version__ = "1.5.8"
__version_info__ = (1, 5, 8)

# Package metadata
__name__ = "zkernel"
__description__ = "A declarative Python kernel that orchestrates 17 subsystems across Terminal and Web contexts"
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


