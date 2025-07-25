FROM python:3.11-slim

WORKDIR /app

COPY config-schema.json entrypoint.py ./

RUN pip install boto3 python-dotenv

COPY download.py /usr/local/bin/download
RUN chmod +x /usr/local/bin/download

COPY upload.py /usr/local/bin/upload
RUN chmod +x /usr/local/bin/upload

RUN pip install jsonschema \
    && chmod +x entrypoint.py

ENTRYPOINT ["python3", "-u", "entrypoint.py"]

