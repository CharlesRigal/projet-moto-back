FROM python:latest
LABEL authors="RigalCh"

EXPOSE 8888

COPY application requirement.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]