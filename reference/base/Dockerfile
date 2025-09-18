FROM python:3.11-slim

RUN apt-get update && apt-get install -y jq && rm -rf /var/lib/apt/lists/*

COPY ./schemas /schemas

RUN pip install boto3 python-dotenv
RUN pip install --no-cache-dir jsonschema>=4.23.0

# Download from S3
COPY download.py /usr/local/bin/download
RUN chmod +x /usr/local/bin/download

# Upload to S3
COPY upload.py /usr/local/bin/upload
RUN chmod +x /usr/local/bin/upload

# Validate Config(s)
COPY validate.py /usr/local/bin/validate
RUN chmod +x /usr/local/bin/validate

# Validate and Download files
COPY download_from_config.py /usr/local/bin/download_from_config
RUN chmod +x /usr/local/bin/download_from_config

ENTRYPOINT ["/usr/local/bin/validate"]