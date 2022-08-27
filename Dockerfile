FROM python:3.8.3-alpine

EXPOSE 9008

ENV  PROMETHEUS_PREFIX solar
ENV  RS485_ADDRESS=192.168.2.40
ENV  RS485_PORT=8899
ENV  PROMETHEUS_PORT 9008
ENV  POLLING_INTERVAL_SECONDS 60

RUN pip install --upgrade pip && pip uninstall serial

COPY files/requirements.txt /app/

WORKDIR /app
RUN pip install -r requirements.txt

RUN mkdir -p /data/backup

COPY files/app* /app/

CMD python ./solarrs485-exporter.py