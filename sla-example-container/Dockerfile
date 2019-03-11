FROM debian:9.8

# This is how to install python 3.7 in Debian. Used because it's currently the most complicated distro to get it on.
# Unrelated (but useful) packages included here:
# dos2unix: Converts CRLF files from Windows into LF files for Unix.
# jq: JSON for bash.
# boto3 and awscli: SDK and CLI for AWS resources.
# ssm-starter: Begin a command in an environment injected with SSM parameters from AWS.

ENV PYTHON_VER 3.7.0

WORKDIR /python

ENV SLARUNNER_COMMAND 'python /scripts/random_nonsense.py'
ENV SLARUNNER_SERVICE random-nonsense-service 
ENV SLARUNNER_GROUPS random-group,testing-group
ENV SLARUNNER_DELAY 15
ENV SLARUNNER_S3BUCKETNAME sla-monitor-runner-logs-dev-us-east-1
ENV SLARUNNER_SNSTOPICNAME sla-monitor-result-published-dev

RUN apt update -y && \
	apt install -y libreadline-dev \
                   build-essential \
                   libncurses5-dev \
                   libgdbm-dev \
                   libnss3-dev \
                   libssl-dev \
                   libffi-dev \
                   dos2unix \
                   zlib1g \
                   tk-dev \
                   make \
                   curl \
                   jq
	
RUN curl https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz | tar xz && \
    cd Python-${PYTHON_VER} && ./configure && make && make install

RUN cd /usr/local/bin && \
    ln -s python3 python && \
    ln -s pip3 pip && \
    ln -s python3-config python-config

RUN cd /home && rm -rf /python && \
    pip install -U pip && \
	pip install -U requests boto3 ssm-starter awscli sla-runner

# Test container stuff now

COPY . /scripts

ENTRYPOINT ["sla-runner"]