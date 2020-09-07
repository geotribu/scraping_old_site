# Crawler et convertir les revues de presse

## Lancer

```powershell
# avec juste les avertissements et erreurs
scrapy crawl geotribu_rdp -L WARNING
# avec le détail des opérations
scrapy crawl geotribu_rdp -L INFO
```

> Les fichiers générés sont stockés dans un dossier `_output` (créé s'il n'existe pas).

## Pas à pas

```python
scrapy shell "https://web.archive.org/web/20170606110634/http://geotribu.net/revues-de-presse"

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
