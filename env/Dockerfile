FROM python:3.5.2

ADD . /tmp
RUN /tmp/bootstrap.sh && pip3 install -vvv -r /tmp/requirements.txt

WORKDIR /opt

