# Installation

## Pré-requis

- Python 3.7 ou 3.8


## Installer

```powershell
# créer un environnement virtuel
py -3.7 -m venv .venv

# installer les dépendances
python -m pip install -U -r requirements.txt

# installer les hooks git
pre-commit install
```

## Configurer l'URL de base

Par défaut, c'est l'URL du site sauvegardé dans l'Internet Archive et accessible via leur [Wayback Machine](https://web.archive.org/) : <https://web.archive.org/web/20170423052005/http://geotribu.net/>.

Pour changer l'URL de base, il suffit de changer la valeur de `DEFAULT_URL_BASE` dans le fichier `settings.py`.
