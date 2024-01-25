FROM python:latest
LABEL authors="RigalCh"

COPY application requirement.txt ./

RUN pip install -r requirement.txt

ENTRYPOINT ["gunicorn", "-w", ]