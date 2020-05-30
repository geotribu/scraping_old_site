# Installation

## Pré-requis

- Python 3.7 ou 3.8
- disposer de l'ancien site déployé sur une URL accessible. URL par défaut : <http://localhost/geotribu_reborn>.

## Installer

```powershell tab="Powershell"
# créer un environnement virtuel
py -3.7 -m venv .venv

# installer les dépendances
python -m pip install -U -r requirements.txt

# installer les hooks git
pre-commit install
```
