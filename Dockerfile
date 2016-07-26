FROM python:3.5.2

WORKDIR /opt

RUN bash bin/bootstrap.sh && pip3 install -vvv -r requirements.txt

