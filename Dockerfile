FROM ubuntu:latest
LABEL authors="mariapogorelova"

FROM python:3.9-slim

WORKDIR /finance_tracker

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=flaskr
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]


