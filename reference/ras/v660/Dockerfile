

FROM registry.access.redhat.com/ubi8/ubi:8.5 AS build

# Enable Python module (needed on RHEL/UBI 8)
RUN yum -y update && \
    yum -y install wget unzip jq

RUN wget https://www.hec.usace.army.mil/software/hec-ras/downloads/Linux_RAS_v66.zip

RUN unzip Linux_RAS_v66.zip
# RUN unzip Linux_RAS_v66/Linux_RAS_v66.zip

FROM registry.access.redhat.com/ubi8/ubi:8.5 AS prod
RUN yum -y install jq python38

RUN pip3.8 install h5py

COPY --from=build /Linux_RAS_v66/ /ras


RUN chmod +x -R ras/*


RUN mkdir /sim
WORKDIR /sim
COPY run-model.sh .
RUN chmod +x run-model.sh
COPY delete_hdf5_group.py .

ENTRYPOINT ["/sim/run-model.sh"]
