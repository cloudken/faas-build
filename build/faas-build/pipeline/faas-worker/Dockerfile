FROM alpine:latest
MAINTAINER Cloudken
RUN mkdir -p /root/temp
COPY cloudframe-*.tar.gz /root/temp/
WORKDIR /root/temp
RUN tar xvfz cloudframe-*.tar.gz
RUN rm -f cloudframe-*.tar.gz
RUN mv cloudframe-* cloudframe
RUN mkdir -p /var/log/cloudframe
#COPY supervisord.conf /etc/supervisord.conf
COPY start.sh /root/start.sh
WORKDIR /
ENTRYPOINT ["/root/start.sh"]
