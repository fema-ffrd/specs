# build using Red Hat UBI8 as the base image
FROM registry.access.redhat.com/ubi8/ubi:8.5 AS build
RUN yum -y update && \
    yum -y install wget && \
    yum -y install unzip && \
    yum -y install jq

RUN wget https://www.hec.usace.army.mil/software/hec-ras/downloads/Linux_RAS_v66.zip

RUN unzip Linux_RAS_v66.zip

# Use the ffrd base image with validation, download, and upload tools
FROM ffrd_base:latest

COPY --from=build /Linux_RAS_v66/ /ras

RUN chmod +x -R ras/*

RUN mkdir /sim
WORKDIR /sim

COPY run_model.py .
ENTRYPOINT ["python", "run_model.py"]