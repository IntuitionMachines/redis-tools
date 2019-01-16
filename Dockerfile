FROM python:3-alpine

WORKDIR /work
VOLUME ["/vol"]

# Install all the common components early on in the process to leverage docker layer caching
RUN sed -i 's/archive/us-west-2\.ec2\.archive/' /etc/apk/repositories \
 && apk update  \
 && apk add libc-dev gcc jq git curl bash \
 && apk add python-dev \
 && apk add py-pip 

COPY requirements.txt /work
RUN pip install -r requirements.txt

COPY bin /work/bin/
COPY *.py /work/
CMD bash