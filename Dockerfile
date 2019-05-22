# Flask recommends:
# Latest version of Python 3. Flask supports Python 3.4 and newer, Python 2.7,
# and PyPy.
FROM python:latest

RUN pip install --upgrade pip

RUN pip install \
Flask \
mysql-connector

COPY .env /.env

# create directory if not available and set as working directory
WORKDIR /web

# in this context, /web is a directory
COPY requirements.txt /web

RUN pip install -r requirements.txt

# Do not use for production
# http://flask.pocoo.org/docs/1.0/config/
#
ENV FLASK_ENV=development

# Specifies port to listen
# Default for Flask framework
EXPOSE 5000

CMD python /web/index.py
