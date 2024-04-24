FROM python:latest
LABEL authors="RigalCh"

EXPOSE 8888

COPY application requirements.txt /src/
WORKDIR /src/

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
