FROM alpine:latest

# Install main O/S applications required
RUN apk add --no-cache \
    curl git sudo vim \
    python3 py3-pip \
    py3-cryptography \
    openssh-client \
    mariadb-client \
    postgresql-client postgresql \
    samba-client \
    gnupg \
    zip unzip

# Install main python packages required
RUN pip3 install \
    boto3 \
    awscli \
    adal \
    azure-mgmt-compute \
    prometheus_client \
    elasticsearch

WORKDIR /opt/backups
COPY . .

RUN python3 setup.py install
ENTRYPOINT ["./docker-entrypoint.sh"]