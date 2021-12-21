# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV BOT_TOKEN=$secrets.BOT_TOKEN

CMD [ "python3", "./main.py" ]
