#! python3  # noqa: E265

"""
    Metadata bout the package to easily retrieve informations about it.
    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

from datetime import date

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]


__title__ = "Geotribu Reborn Scraper"
__summary__ = (
    "Outillage de web-scraping utilisé pour récupérer les contenus de "
    "l'ancien site de Geotribu et les convertir en markdwon."
)
__uri__ = "https://github.com/geotribu/scraping_old_site/"

__version__ = "0.9.0"

__author__ = "Julien M. (@geoJulien/Twitter, @Guts/Github) pour Geotribu"
__email__ = "geotribu@gmail.com"

__license__ = "GNU Lesser General Public License v3.0"
__copyright__ = "2020 - {0}, {1}".format(date.today().year, __author__)
