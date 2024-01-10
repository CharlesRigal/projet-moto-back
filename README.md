#projet-moto-back

Pour installer le projet

```
> python -m venv venv

> ./venv/Scripts/activate

(venv) > pip install -r requirements.txt
```

Pour démarrer le developpement

```
> ./venv/Scripts/activate

(venv) > cd application

(venv) > uvicorn main:app --reload
```

Pour modifier la base de données

```
(venv) > alembic revision --autogenerate -m

aller recuperer l'id de la migration qui vient d'être crée dans application/alembic/versions

(venv) > alembic upgrade {id}
```