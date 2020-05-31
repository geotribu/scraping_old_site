# Crawler et convertir les articles

## Lancer

```powershell
# avec juste les avertissements et erreurs
scrapy crawl geotribu_articles -L WARNING
# avec le détail des opérations
scrapy crawl geotribu_articles -L INFO
```

> Les fichiers générés sont stockés dans un dossier `_output` (créé s'il n'existe pas).
