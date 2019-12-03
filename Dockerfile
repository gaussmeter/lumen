FROM balenalib/rpi-alpine:3.6
RUN [ "cross-build-start" ]
RUN apk update && \
    apk add --no-cache 'python3=3.6.8-r0' && \
    apk add --no-cache --virtual build \
                       gcc \
                       make \
                       libc-dev \
                       linux-headers \
                       python3-dev && \
    pip3 --disable-pip-version-check --no-cache-dir install rpi_ws281x \
                                                            adafruit-circuitpython-neopixel \
                                                            RPi.GPIO && \
    apk del build && \
    rm -v /var/cache/apk/*
RUN [ "cross-build-end" ]
ADD lumen.py lumen.py
CMD /usr/bin/python3 -u ./lumen.py
