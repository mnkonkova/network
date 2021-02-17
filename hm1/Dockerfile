FROM ubuntu:18.04

RUN apt-get update && apt-get install -y apt-utils
RUN apt-get install -y python3
COPY server.py server.py
COPY client.py client.py
COPY run.sh run.sh
RUN chmod +x run.sh

ENTRYPOINT ./run.sh