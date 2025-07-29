# TODO: Add version metadata for each upstream container
FROM hms-ffrd AS hms_builder
FROM ras-ffrd AS ras_builder
FROM ffrd_base AS prod

RUN apt update && apt -y install wget unzip libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1

# Copy HMS artifacts
COPY --from=hms_builder /HEC-HMS-4.11 /HEC-HMS-4.11
COPY --from=hms_builder /HEC-HMS-4.11/lib/hms-compute.jar /app/build/libs/hms-compute.jar
COPY --from=hms_builder /app/run_hms.sh /app/run_hms.sh
RUN chmod +x /HEC-HMS-4.11/jre/bin/java
RUN chmod +x /app/run_hms.sh

ENV HMS_HOME=/HEC-HMS-4.11
ENV JAVA_EXE=/HEC-HMS-4.11/jre/bin/java
ENV JAVA_HOME=/HEC-HMS-4.11/jre
ENV PROG=hms.hms
ENV PATH=/HEC-HMS-4.11/bin/taudem:/HEC-HMS-4.11/bin/mpi:/HEC-HMS-4.11/bin:/HEC-HMS-4.11/jre/bin/:/HEC-HMS-4.11/bin/:/HEC-HMS-4.11/jre/lib/:$PATH
ENV GDAL_DATA=/HEC-HMS-4.11/bin/gdal/gdal-data
ENV PROJ_LIB=/HEC-HMS-4.11/bin/gdal/proj
ENV CLASSPATH=/HEC-HMS-4.11/*:/HEC-HMS-4.11/lib/*:/HEC-HMS-4.11/lib/hec/*:/HEC-HMS-4.11/jre/lib/*
ENV JAVA_OPTS="-Djava.library.path=/HEC-HMS-4.11/bin/gdal:/HEC-HMS-4.11/bin"

# Copy RAS artifacts
COPY --from=ras_builder /ras/libs /ras/libs
COPY --from=ras_builder /ras/v61 /ras/v61
COPY --from=ras_builder /sim/run-model.sh /sim/run-model.sh
COPY --from=ras_builder /sim/run-model.sh /usr/local/bin/run-ras-model
RUN chmod +x /usr/local/bin/run-ras-model

# Set environment variables from file
COPY  hms_schema.json /schemas/hms_schema.json
COPY  ras_schema.json /schemas/ras_schema.json
COPY .env.runtime /tmp/env
RUN set -a && . /tmp/env && set +a && rm /tmp/env

COPY entrypoint_conformance.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint_conformance.sh

ENTRYPOINT ["/usr/local/bin/entrypoint_conformance.sh"]
