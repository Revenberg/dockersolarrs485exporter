#!/bin/bash

# version 2022-08-26 15:20

cd /home/pi/dockersolarrs485exporter

if [ -n "$1" ]; then
  ex=$1
else
  rc=$(git remote show origin |  grep "local out of date" | wc -l)
  if [ $rc -ne "0" ]; then
    ex=true
  else
    ex=false
  fi
fi

if [ $ex == true ]; then
    git pull
    chmod +x build.sh

    docker image build -t revenberg/solarrs485exporter:latest .

    #docker push revenberg/solarrs485exporter:latest

    # testing: 

    echo "==========================================================="
    echo "=                                                         ="
    echo "= docker-compose up                                       ="
    echo "=                                                         ="
    echo "==========================================================="

    docker-compose up
fi

cd -