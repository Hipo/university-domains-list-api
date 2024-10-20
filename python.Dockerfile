FROM python:3.11.2 as base

RUN apt update && apt install -y --no-install-recommends --fix-missing openssh-server

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
WORKDIR /university-domains-list-api
