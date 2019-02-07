FROM python:3.7

LABEL maintainer="Arne Recknagel"

COPY wheel/* wheel/
COPY logger_config.json .

RUN pip install wheel/*

CMD [ "echo", "Run c11h-dataclassutils-code here" ]
