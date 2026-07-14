FROM alpine:3.19

RUN apk add --no-cache \
    bash \
    curl \
    gzip \
    tar \
    aws-cli \
    mongodb-tools

COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

COPY crontab /etc/crontabs/root

CMD ["crond", "-f", "-l", "2"]
