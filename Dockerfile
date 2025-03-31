ARG BASE_IMAGE=${SPARK_BASE_IMAGE:?}

FROM $BASE_IMAGE

COPY . /brewery/

WORKDIR /brewery

RUN pip3 install --no-cache-dir .

ENTRYPOINT [ "brewery-cli" ]
CMD [ "--help" ]
