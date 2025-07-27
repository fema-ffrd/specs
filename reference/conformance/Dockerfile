# FROM hms-ffrd AS hms_builder
# Add version metadata for each upstream container
FROM ras-ffrd AS ras_builder
FROM ffrd_base AS prod

# Copy HMS artifacts
# COPY --from=hms_builder /HEC-HMS-4.11 /HEC-HMS-4.11
# COPY --from=hms_builder /HEC-HMS-4.11/lib/hms-compute.jar /app/build/libs/hms-compute.jar
# COPY --from=hms_builder /app/schema-extension.json /app/schema-extension.json
# COPY --from=hms_builder /app/run_hms.py /app/run_hms.py

# Copy RAS artifacts
COPY --from=ras_builder /ras/libs /ras/libs
COPY --from=ras_builder /ras/v61 /ras/v61
COPY --from=ras_builder /sim/run-model.sh /sim/run-model.sh
COPY --from=ras_builder /sim/run-model.sh /usr/local/bin/run-ras-model
RUN chmod +x /usr/local/bin/run-ras-model

# Set environment variables from file
COPY  ras_schema.json /schemas/ras_schema.json
COPY .env.runtime /tmp/env
RUN set -a && . /tmp/env && set +a && rm /tmp/env

COPY entrypoint_conformance.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint_conformance.sh

ENTRYPOINT ["/usr/local/bin/entrypoint_conformance.sh"]
