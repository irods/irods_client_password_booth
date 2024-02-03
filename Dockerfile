FROM python:3.12

RUN pip install cherrypy python-irodsclient

ADD app.css /
ADD app.py /

ENTRYPOINT ["python", "app.py"]
