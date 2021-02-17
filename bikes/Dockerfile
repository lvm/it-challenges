FROM alpine:edge
MAINTAINER Mauro <mauro@sdf.org>

ENV LIBRARY_PATH=/lib:/usr/lib

ADD [".", "/srv/bikes/"]
COPY ["init-scripts/api.run", "/etc/service/api/run"]
COPY ["init-scripts/admin.run", "/etc/service/admin/run"]
COPY ["init-scripts/nginx.run", "/etc/service/nginx/run"]

RUN touch /etc/inittab \
    && apk --update add ca-certificates python3 runit nginx \
    && mkdir -p /run/nginx/ \
    && python3 -m ensurepip && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip; fi \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && rm -r /root/.cache \
    && rm -rf /var/cache/apk/* \
    && pip install -r /srv/bikes/requirements.pip \
    && chmod 755 /etc/service/api/run \
    && chmod 755 /etc/service/admin/run \
    && chmod 755 /etc/service/nginx/run \
    && python /srv/bikes/startup.py --init

COPY ["conf/nginx.conf", "/etc/nginx/conf.d/default.conf"]

EXPOSE 81
EXPOSE 82

CMD ["/sbin/runsvdir", "-P", "/etc/service"]
