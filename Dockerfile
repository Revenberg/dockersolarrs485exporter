FROM python:alpine3.7

EXPOSE 9003

ENV  PROMETHEUS_PREFIX solarrs485exporter
ENV  IP ""
ENV  PROMETHEUS_PORT 9008
ENV  POLLING_INTERVAL_SECONDS 60

RUN pip install --upgrade pip && pip uninstall serial

COPY files/requirements.txt /app/

WORKDIR /app
RUN pip install -r requirements.txt

RUN mkdir -p /data/backup

COPY files/app* /app/

CMD python ./solarrs485-exporter.py