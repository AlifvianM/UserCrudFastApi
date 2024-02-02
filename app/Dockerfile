FROM python:3.10-slim

WORKDIR /app_backend

COPY ./requirements.txt /app_backend/requirements.txt

# RUN apt-get update \
#     && apt-get install gcc -y \
#     && apt-get clean

RUN python -m pip install --upgrade pip \
    && pip install -r /app_backend/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /app_backend/    