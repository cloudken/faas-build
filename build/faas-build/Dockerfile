from alpine:latest
MAINTAINER Husong
RUN ["/bin/sh", "-c", "apk add --repository http://mirrors.zte.com.cn/alpine/v3.6/main/ --allow-untrusted --no-cache python python-dev py-pip gcc g++ linux-headers musl-dev ansible"]
RUN mkdir -p /root/temp
COPY cloudframe-*.tar.gz /root/temp/
WORKDIR /root/temp
RUN tar xvfz cloudframe-*.tar.gz
RUN rm -f cloudframe-*.tar.gz
RUN mv cloudframe-* cloudframe
WORKDIR /root/temp/cloudframe
RUN mkdir -p /root/.pip
COPY pip.conf /root/.pip/
RUN ["/bin/sh", "-c", "pip install -U pip"]
RUN ["/bin/sh", "-c", "pip install -U setuptools"]
RUN ["/bin/sh", "-c", "pip install supervisor"]
RUN ["/bin/sh", "-c", "pip install -r requirements.txt"]
RUN ["/bin/sh", "-c", "python setup.py install --user"]
RUN rm -rf /usr/lib/gcc
RUN rm -rf /usr/share
RUN rm -rf /usr/libexec
RUN rm -rf /usr/x86_64-alpine-linux-musl
RUN rm -rf /usr/include
RUN rm -rf /usr/lib/libc.a
COPY supervisord.conf /etc/supervisord.conf
RUN mkdir -p /var/log/cloudframe
RUN rm -rf /root/temp
RUN mkdir -p /root/faas
COPY pipeline /root/faas/pipeline
COPY ansible.cfg /root/.ansible.cfg
WORKDIR /
ENTRYPOINT ["/usr/bin/supervisord"]
