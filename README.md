# Outillage de récupération de l'ancien site de GeoTribu

![Python quality basics](https://github.com/geotribu/scraping_old_site/workflows/Python%20quality%20basics/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/geotribu-web-scraping-resurrection/badge/?version=latest)](https://geotribu-web-scraping-resurrection.readthedocs.io/)

L'objectif est de récupérer le contenu depuis l'ancien site de Geotribu (2007-2015) pour l'intégrer au [nouveau site basé sur MkDocs et dont le contenu est donc en markdown](https://github.com/geotribu/website).

Deux volets au projet :

- [web scraping](https://fr.wikipedia.org/wiki/Web_scraping) avec [Scrapy](https://scrapy.org/)
- conversion et export des contenus en markdown avec [markdownify](https://pypi.org/project/markdownify/)

Pour plus d'infos techniques, [consulter la documentation](https://geotribu-web-scraping-resurrection.readthedocs.io/).

## Pré-requis

- Python 3.7+
- disposer de l'ancien site déployé sur une URL accessible. URL par défaut : <http://localhost/geotribu_reborn>.
