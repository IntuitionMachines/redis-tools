FROM python:3.7.2-alpine3.7

WORKDIR /work

# Redis for testing
ENV REDISHOST "redis"
ENV REDIS_SSL "False"

# Install all the common components early on in the process to leverage docker layer caching
RUN apk --update add jq git curl bash py3-pip python3-dev gcc libc-dev

COPY requirements.txt /work
RUN pip install -r requirements.txt

COPY bin /work/bin/
COPY redistools /work/redistools
COPY tests /work/tests
CMD bash
