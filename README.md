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
(venv) > alembic revision --autogenerate

aller recuperer l'id de la migration qui vient d'être crée dans application/alembic/versions

(venv) > alembic upgrade {id}
```

Variable pour le fichier .env
```
DATABASE_URL=postgresql+psycopg2://******:*****@***.*.*.*:****/********
JWT_SECRET_KEY=****************************
JWT_ALGORITHM=*****
JWT_EXPIRE_HOURS=****
ENV=development|production
TEST_DATABASE_USER=username
TEST_DATABASE_PASSWORD=password
```