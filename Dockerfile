# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV BOT_TOKEN=1266964486:AAHG88-GRJn7Ow5dAtKD7_MpJIK5ivsPQAE

CMD [ "python3", "./main.py" ]
