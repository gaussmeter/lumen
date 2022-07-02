FROM balenalib/rpi-alpine:3.15
RUN [ "cross-build-start" ]
RUN apk update && \
    apk add --no-cache python3=3.9.7-r4 && \
    apk add --no-cache --virtual build \
                       gcc=10.3.1_git20211027-r0 \
                       make=4.3-r0 \
                       libc-dev=0.7.2-r3 \
                       linux-headers=5.10.41-r0 \
                       python3-dev=3.9.7-r4 \
                       py3-pip=20.3.4-r1 && \
    pip --disable-pip-version-check --no-cache-dir install rpi_ws281x==4.2.4 \
                                                           adafruit-circuitpython-neopixel==6.3.3 \
                                                           RPi.GPIO==0.7.1 && \
    apk del build && \
    rm -v /var/cache/apk/*
RUN [ "cross-build-end" ]
ADD lumen.py lumen.py
CMD /usr/bin/python3 -u ./lumen.py
