FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/home/code/ PYTHONHASHSEED=0
ENV API_HOST=0.0.0.0
ENV API_PORT=8080

COPY ./requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r requirements.txt

WORKDIR /usr/src/users

COPY ./app/ app/
COPY ./main.py .env ./

CMD python3 main.py