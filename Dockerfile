FROM python:latest
LABEL authors="RigalCh"

EXPOSE 8888
WORKDIR /src/

COPY requirements.txt application ./

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
