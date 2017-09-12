FROM python:2.7-wheezy
LABEL maintainer "MIT CLIx Tech Team <clix-tech@mit.edu>"

WORKDIR /tmp

# Ideally memcached would be a separate Docker container,
#   but currently dlkit assumes it runs on the same host
CMD ["apt-get", "install", "memcached"]

COPY requirements.txt /tmp/requirements.txt
COPY test_requirements.txt /tmp/test_requirements.txt
RUN pip install -r requirements.txt -r test_requirements.txt

RUN mkdir /qbank
COPY . /qbank
WORKDIR /qbank

EXPOSE 8080

CMD ["python", "main.py"]
