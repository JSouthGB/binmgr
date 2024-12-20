FROM debian:bullseye as builder
RUN groupadd -g 1000 binmgr && \
    useradd -m -u 1000 -g binmgr binmgr

WORKDIR /app
RUN apt-get update && apt-get install -y \
    wget \
    gcc \
    make \
    python3-dev \
    zlib1g-dev \
    libz-dev \
    libbz2-dev \
    libssl-dev \
    libffi-dev \
    build-essential \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

# build static zlib
RUN wget https://zlib.net/fossils/zlib-1.2.13.tar.gz && \
    tar xf zlib-1.2.13.tar.gz && \
    cd zlib-1.2.13 && \
    CFLAGS="-fPIC" ./configure --static && \
    make && \
    make install

# build python
RUN wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz && \
    tar xf Python-3.9.18.tgz && \
    cd Python-3.9.18 && \
    ./configure \
        --prefix=/usr/local/python3.9-static \
        --enable-shared \
        LDFLAGS="-Wl,-rpath=/usr/local/python3.9-static/lib" && \
    make && \
    make install

COPY ./src /app
COPY ./binmgr.spec /app/
RUN chown -R binmgr:binmgr /app
USER binmgr

ENV PATH="/usr/local/python3.9-static/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/python3.9-static/lib"

RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install pyinstaller
RUN venv/bin/pip install -r requirements.txt
