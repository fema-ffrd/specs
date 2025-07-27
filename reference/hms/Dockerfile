FROM gradle:7.3.1-jdk17 as javabuilder

USER root
RUN apt update && apt -y install wget unzip libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1

WORKDIR /app
COPY ./src /app/src
COPY ./build.gradle /app
COPY ./gradlew /app
COPY ./schema-extension.json /app

# HMS binaries and supporting libraries from HEC
RUN wget https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hec-hms/4.11-linux64/hec-hms-4.11-linux64.tar.gz \
    && tar -xvzf hec-hms-4.11-linux64.tar.gz \
    && rm hec-hms-4.11-linux64.tar.gz

# Build the jar
RUN gradle build --no-daemon \
    && chmod +x /app/build/libs/hms-compute.jar

# Final stage: create the production container
FROM ffrd_base as prod
RUN apt update && apt -y install libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1

COPY --from=javabuilder /app/HEC-HMS-4.11 /HEC-HMS-4.11
COPY --from=javabuilder /app/build/libs/hms-compute.jar /HEC-HMS-4.11/lib
COPY --from=javabuilder /app/schema-extension.json /app/schema-extension.json

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

WORKDIR /app
COPY ./run_hms.py /app

# Install jq to allow JSON schema merging
RUN apt-get update && apt-get install -y jq && rm -rf /var/lib/apt/lists/*

# Merge base config-schema.json with the extension
RUN jq -s '.[0] * .[1]' /app/config-schema.json /app/schema-extension.json > /app/config-schema.merged.json \
    && mv /app/config-schema.merged.json /app/config-schema.json
    # && rm /app/schema-extension.json


COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
