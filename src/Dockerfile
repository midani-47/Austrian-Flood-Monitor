# Dockerfile for Flask
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

###########START NEW IMAGE : DEBUGGER ###################
FROM base as debug

RUN pip install debugpy

CMD python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m flask run -h 0.0.0.0 -p 5000

###########START NEW IMAGE: PRODUCTION ###################
FROM base as prod

CMD gunicorn manage:app --reload --config gunicorn.conf.py
