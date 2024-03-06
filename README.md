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
DATABASE_URL=postgresql+psycopg2://postgres:admin@127.0.0.1:5432/moto-dev
JWT_SECRET_KEY=IDFUHQSFIHZILSEDFHIDFHQSDFBNQI/*
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8760
ENV=development
