FROM python:3.11-slim

ENV HECSTAC_VERSION=0.3.0

WORKDIR /app

COPY hecstac_schema.json .
COPY ./data /mnt

RUN pip install python-dotenv hecstac==${HECSTAC_VERSION}
RUN apt-get update && apt-get install -y libexpat1

COPY ras_metadata.py /usr/local/bin/ras_metadata
RUN chmod +x /usr/local/bin/ras_metadata

ENTRYPOINT ["/usr/local/bin/ras_metadata"]