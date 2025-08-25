FROM registry.access.redhat.com/ubi8/ubi:8.5 AS build
RUN yum -y update && \
    yum -y install wget && \
    yum -y install unzip && \
    yum -y install jq

RUN wget https://www.hec.usace.army.mil/software/hec-ras/downloads/Linux_RAS_v66.zip

RUN unzip Linux_RAS_v66.zip
# RUN unzip Linux_RAS_v66/Linux_RAS_v66.zip

FROM registry.access.redhat.com/ubi8/ubi:8.5 AS prod
RUN yum -y install jq

COPY --from=build /Linux_RAS_v66/ /ras


RUN chmod +x -R ras/*


RUN mkdir /sim
WORKDIR /sim
COPY run-model.sh .
RUN chmod +x run-model.sh

ENTRYPOINT ["/sim/run-model.sh"]