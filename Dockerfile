FROM python:3.5

RUN apt update -y && \
    apt install -y pandoc && \
    pip install twine pypandoc

WORKDIR /src

COPY . .

RUN pip install -e .

RUN chmod +x $(find . -iname '*.sh')

# This allows logs to be in realtime instead of
# buffering all the python output at the end.
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf8

# ENTRYPOINT ["/bin/bash", "-c"]
# CMD ["sla-runner", "run",
#      "--command",   "$SLARUNNER_COMMAND", 
#      "--service",   "$SLARUNNER_SERVICE",
#      "--live-url",  "$SLARUNNER_LIVEURL"
#      "--delay",     "$SLARUNNER_DELAY",
#      "--sns-topic", "$SLARUNNER_SNSTOPIC",
#      "--s3-bucket-name", "$SLARUNNER_S3BUCKETNAME"]

ENTRYPOINT ["sla-runner"]
