# Crawler et convertir les articles

URL pour les articles : <https://web.archive.org/web/20170222060359/http://www.geotribu.net/articles-blogs>.

## Lancer

```powershell
# avec juste les avertissements et erreurs
scrapy crawl geotribu_articles -L WARNING
# avec le détail des opérations
scrapy crawl geotribu_articles -L INFO
```

> Les fichiers générés sont stockés dans un dossier `_output` (créé s'il n'existe pas).
