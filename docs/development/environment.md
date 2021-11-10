# Environnement de développement

Sur Ubuntu :

```bash
# create virtual environment
python3.8 -m venv .venv
source .venv/bin/activate

# bump dependencies inside venv
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements.txt

# install project as editable
python -m pip install -e .
```
