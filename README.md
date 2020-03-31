# Outillage de récupération de l'ancien site de GeoTribu

L'objectif est de récupérer le contenu depuis l'ancien site de Geotribu (2007-2015) pour l'intégrer au [nouveau site basé sur MkDocs et dont le contenu est donc en markdown](https://github.com/geotribu/website).

Deux volets au projet :

- [web scraping](https://fr.wikipedia.org/wiki/Web_scraping) avec [Scrapy](https://scrapy.org/)
- conversion et export des contenus en markdown

## Pré-requis

- Python 3.7
- disposer de l'ancien site déployé sur une URL accessible. URL par défaut : <http://localhost/geotribu_reborn>.

## Installer

```powershell tab="Powershell"
# créer un environnement virtuel
py -3.7 -m venv .venv

# installer les dépendances
python -m pip install -U -r requirements.txt
```

## Lancer

Les fichiers générés sont stockés dans un dossier `_output` créé à la volée.

### Revues de presse

```powershell
scrapy crawl geotribu_rdp
```

Ou pas à pas :

```python
scrapy shell "http://localhost/geotribu_reborn/revues-de-presse"

# titre de la page
response.css('title::text').getall()[0]

# première rdp de la liste
t = response.css('div.title-and-meta')[0]
t = response.css('article')[0]

# date
rdp_date = t.css("div.date")
rdp_date_day = rdp_date.css("span.day::text").get()
rdp_date_month = rdp_date.css("span.month::text").get()
rdp_date_year = rdp_date.css("span.year::text").get()

# title
rdp_title_section = t.css("div.title-and-meta")
rdp_title = rdp_title_section.css("h2.node__title a::text").get()

# url
rdp_url_rel = rdp_title_section.css("h2.node__title a::attr(href)").get()

# -- Parcourir la revue de presse

fetch("http://localhost" + rdp_url_rel)

# contenu de la rdp
rdp = response.css('article')[0]

# title
rdp_title_section = t.css("div.title-and-meta")
rdp_title = rdp_title_section.css("h2.node__title a::text").get()

# sections
rdp_sections = rdp.css("p.typeNews::text").getall()
```
