FROM registry.access.redhat.com/ubi8/ubi:8.5 AS build
RUN yum -y update && \
    yum -y install wget unzip jq && \
    yum -y clean all

RUN wget https://www.hec.usace.army.mil/software/hec-ras/downloads/Linux_RAS_v66.zip
RUN unzip Linux_RAS_v66.zip


FROM ffrd_base:latest AS ffrd_base

COPY --from=build /Linux_RAS_v66/ /ras
RUN chmod +x -R /ras/*

RUN mkdir /sim
WORKDIR /sim

COPY run_model.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

COPY parsers/ras_unsteady.py ./parsers/ras_unsteady.py

ENTRYPOINT ["./entrypoint.sh"]