import subprocess
import sys


HMSFilePath="/app/trinity.hms"
SimulationName="SST"

print("")
print("---------Run HMS Simulation----------")
print("")
print(f"Sending {HMSFilePath} to hms-compute")

cmd = [
    "java",
    "-XX:+ExitOnOutOfMemoryError",
    "-XX:MaxRAMPercentage=75",
    "-XX:+UseContainerSupport",
    "-Djava.library.path=/HEC-HMS-4.11/bin/gdal:/HEC-HMS-4.11/bin",
    "-jar",
    "/HEC-HMS-4.11/lib/hms-compute.jar",
    HMSFilePath,
    SimulationName
]

try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"hms-compute error: {e}", file=sys.stderr)
    sys.exit(1)


# apt install unzip && unzip /HEC-HMS-4.11/samples.zip -d /tmp && cp -r /tmp/samples/* /app