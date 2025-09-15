

FROM registry.access.redhat.com/ubi8/ubi:8.5 AS build

# Enable Python module (needed on RHEL/UBI 8)
RUN yum -y update && \
    yum -y install wget unzip jq

# FROM registry-public.hecdev.net/hec-ras-linux:6.4.1
RUN wget https://www.hec.usace.army.mil/nexus/repository/cloud-wat-resources/ras/HEC-RAS_641_Linux_EngineOnly.zip
RUN unzip HEC-RAS_641_Linux_EngineOnly.zip


FROM registry.access.redhat.com/ubi8/ubi:8.5 AS prod
RUN yum -y install jq python38

RUN pip3.8 install h5py

COPY --from=build /RAS_641_Linux_EngineOnly/ /ras


RUN chmod +x -R ras/*


RUN mkdir /sim
WORKDIR /sim
COPY run-model.sh .
RUN chmod +x run-model.sh
COPY delete_hdf5_group.py .

ENTRYPOINT ["/sim/run-model.sh"]
