FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04
LABEL maintainer="madhavi.kannan@tempus.com"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        build-essential \
        openslide-tools \
        python3 \
        python3-pip \
        python3-dev \
        python3-setuptools \
        && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*


COPY requirements.txt /opt/ml/requirements.txt

RUN pip3 --no-cache-dir install -r /opt/ml/requirements.txt && \
	rm -rf /root/.cache

COPY src/ /opt/ml/src/

ENV PATH /opt/ml/src:$PATH

ARG BUILD_DATE=undefined
ARG GIT_HASH=research
ENV GIT_HASH="${GIT_HASH}"
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

CMD ["run"]

