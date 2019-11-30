FROM balenalib/rpi-alpine
RUN [ "cross-build-start" ]
RUN apk add --no-cache python3 && \
    apk add --no-cache --virtual build \
                       gcc \
                       make \
                       libc-dev \
                       linux-headers \
                       python3-dev && \
    pip3 --disable-pip-version-check --no-cache-dir install rpi_ws281x \
                                                            adafruit-circuitpython-neopixel \
                                                            RPi.GPIO && \
    apk del build
RUN [ "cross-build-end" ]
ADD lumen.py lumen.py
CMD /usr/bin/python3 -u ./lumen.py
