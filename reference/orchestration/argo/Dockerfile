FROM ffrd_base

WORKDIR /app

# Install PyYAML
RUN pip install --no-cache-dir pyyaml

# Copy schemas
COPY orchestration/argo/schemas/workflow.json /schemas/workflow.json
COPY hms/hms-golang/schemas/action.hms.run_simulation.json /schemas/action.hms.run_simulation.json
COPY ras/v660/schemas/action.ras.run_unsteady_simulation.json /schemas/action.ras.run_unsteady_simulation.json

# Copy the compile script
COPY orchestration/argo/compile_workflow.py /usr/local/bin/compile-workflow
RUN chmod +x /usr/local/bin/compile-workflow

# Copy entrypoint
COPY orchestration/argo/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
