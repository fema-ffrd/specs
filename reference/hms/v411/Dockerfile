FROM gradle:7.3.1-jdk17 as javabuilder

USER root
RUN apt update && apt -y install wget unzip libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1

WORKDIR /app
COPY ./src /app/src
COPY ./build.gradle /app
COPY ./gradlew /app

# HMS binaries and supporting libraries from HEC
RUN wget https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hec-hms/4.11-linux64/hec-hms-4.11-linux64.tar.gz \
    && tar -xvzf hec-hms-4.11-linux64.tar.gz \
    && rm hec-hms-4.11-linux64.tar.gz

# Build the jar
RUN gradle build --no-daemon \
    && chmod +x /app/build/libs/hms-compute.jar

# Final stage: create the production container
FROM python:3.11-slim as prod
RUN apt update && apt -y install jq unzip libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1

COPY --from=javabuilder /app/HEC-HMS-4.11 /HEC-HMS-4.11
COPY --from=javabuilder /app/build/libs/hms-compute.jar /HEC-HMS-4.11/lib

ENV HMS_HOME=/HEC-HMS-4.11
ENV JAVA_EXE=$HMS_HOME/jre/bin/java
ENV JAVA_HOME=$HMS_HOME/jre
ENV PROG=hms.hms
ENV PATH=$HMS_HOME/bin/taudem:$HMS_HOME/bin/mpi:$HMS_HOME/bin:$HMS_HOME/jre/bin/:$HMS_HOME/bin/:$HMS_HOME/jre/lib/:$PATH
ENV GDAL_DATA=$HMS_HOME/bin/gdal/gdal-data
ENV PROJ_LIB=$HMS_HOME/bin/gdal/proj
ENV CLASSPATH=$HMS_HOME/*:$HMS_HOME/lib/*:$HMS_HOME/lib/hec/*:$HMS_HOME/jre/lib/*
ENV JAVA_OPTS="-Djava.library.path=/HEC-HMS-4.11/bin/gdal:/HEC-HMS-4.11/bin"

RUN chmod +x /HEC-HMS-4.11/jre/bin/java

# Unzip samples.zip to /data
RUN mkdir -p /data && unzip /HEC-HMS-4.11/samples.zip -d /data

WORKDIR /app
COPY ./run_hms.sh .
RUN chmod +x run_hms.sh
COPY ./hms_schema.json /schemas