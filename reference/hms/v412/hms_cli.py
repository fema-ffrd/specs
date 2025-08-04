#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
import os
import sys
import json
from time import sleep
import threading
from glob import glob
from datetime import datetime
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'source': getattr(record, 'source', None),
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, 'source'):
            record.source = "-"
        return super().format(record)


def configure_logging(log_format: str):
    handler = logging.StreamHandler(sys.stdout)
    if log_format == 'json':
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter('%(asctime)s - %(levelname)s - %(source)s - %(message)s')
    handler.setFormatter(formatter)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )

logger = logging.getLogger(__name__)


JYTHON_TEMPLATE = '''from hms.model.JythonHms import *
OpenProject("{project_name}", "{project_dir}")
ComputeRun("{sim_name}")
SaveAllProjectComponents()
'''


def stream_tail(path):
    proc = subprocess.Popen(
        ['tail', '-n', '0', '-F', str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1, # Line-buffered output
    )
    with proc.stdout:
        for line in proc.stdout:
            l = line.strip()
            if not l:
                continue
            elif "WARNING" in l:
                logger.warning(l, extra={'source': path})
            elif "NOTE" in l:
                logger.info(l, extra={'source': path})
            elif "ERROR" in l:
                logger.error(l, extra={'source': path})
            else:
                logger.info(l, extra={'source': path})


def main():
    parser = argparse.ArgumentParser(description="HEC-HMS CLI Runner")
    parser.add_argument('--project-file', type=str, help='Path to the .hms project file')
    parser.add_argument('--sim-name', type=str, help='Simulation name to run')
    parser.add_argument('--example', choices=['tenk'], help='Run a built-in example project')
    parser.add_argument('--json-file', type=str, help='Path to a JSON file with hms_schema')
    parser.add_argument('--log-format', type=str, default='text', choices=['text', 'json'], help='Log format (default: text)')
    args = parser.parse_args()

    configure_logging(args.log_format)

    input_methods = sum([bool(args.example), bool(args.json_file), bool(args.project_file and args.sim_name)])
    if input_methods != 1:
        logger.error("Error: Specify exactly one input method: --example, --json-file, or both --project-file and --sim-name.")
        return 1

    if args.example == 'tenk':
        hms_file = "/app/HEC-HMS-4.12/samples/tenk/tenk.hms"
        sim_name = "Jan 96 storm"
    elif args.json_file:
        try:
            with open(args.json_file, 'r') as jf:
                data = json.load(jf)
            hms_schema = data.get('hms_schema', {})
            hms_file = hms_schema.get('project_file')
            sim_name = hms_schema.get('sim_name')
        except Exception as e:
            logger.error(f"Error reading or parsing JSON: {e}")
            return 1
        if not hms_file or not sim_name:
            logger.error("JSON must contain hms_schema with project_file and sim_name.")
            return 1
    else:
        hms_file = args.project_file
        sim_name = args.sim_name

    if not hms_file or not hms_file.lower().endswith('.hms'):
        logger.error("Error: project_file must be a .hms file")
        return 1
    project_dir = os.path.dirname(os.path.abspath(hms_file))
    project_name = os.path.splitext(os.path.basename(hms_file))[0]

    # Generate the Jython script
    jython_script = JYTHON_TEMPLATE.format(
        project_name=project_name,
        project_dir=project_dir,
        sim_name=sim_name
    )
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.script') as f:
        f.write(jython_script)
        script_path = f.name

    # Build the Java command
    hms_home = os.path.abspath('./HEC-HMS-4.12')
    java_exe = os.path.join(hms_home, 'jre', 'bin', 'java')
    classpath = f"{hms_home}/*:{hms_home}/lib/*"
    java_cmd = [
        java_exe,
        '-DMapPanel.NoVolatileImage=true',
        '-Xms32M',
        '-Dpython.path=',
        '-Dpython.home=.',
        '-Djava.library.path=' + hms_home + '/bin:' + hms_home + '/bin/gdal',
        '-classpath', classpath,
        'hms.Hms',
        '-s', script_path
    ]

    # Set up environment variables
    env = os.environ.copy()
    env['PATH'] = f"{hms_home}/bin/taudem:{hms_home}/bin/mpi:" + env.get('PATH', '')
    env['GDAL_DATA'] = f"{hms_home}/bin/gdal/gdal-data"
    env['PROJ_LIB'] = f"{hms_home}/bin/gdal/proj"

    log_files = glob(str(project_dir) + '/*.log') + glob(str(project_dir) + '/*.out')
    for log_file in log_files:
        threading.Thread(target=stream_tail, args=(log_file,), daemon=True).start()

    # Run the Java process
    try:
        proc = subprocess.Popen(java_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        with proc.stdout:
            for line in proc.stdout:
                logger.info(line.strip())
        proc.wait()
        logger.info(f"Simulation '{sim_name}' completed successfully for project '{project_name}' in directory '{project_dir}'.")
        return proc.returncode
    finally:
        sleep(1)  # Allow some time for log threads to finish
        os.remove(script_path)

if __name__ == "__main__":
    returncode = main()
    sys.exit(returncode)
