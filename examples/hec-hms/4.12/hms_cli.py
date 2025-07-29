#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
import os
import sys

# Defaults for the tenk example
TENK_PROJECT_DIR = "/app/HEC-HMS-4.12/samples/tenk"
TENK_PROJECT_NAME = "tenk"
TENK_SIM_NAME = "Jan 96 storm"

JYTHON_TEMPLATE = '''from hms.model.JythonHms import *
OpenProject("{project_name}", "{project_dir}")
ComputeRun("{sim_name}")
SaveAllProjectComponents()
'''

def main():
    parser = argparse.ArgumentParser(description="HEC-HMS CLI Runner")
    parser.add_argument('--project-dir', type=str, help='Path to the HEC-HMS project directory')
    parser.add_argument('--project-name', type=str, help='HEC-HMS project name')
    parser.add_argument('--sim-name', type=str, help='Simulation name to run')
    parser.add_argument('--example', choices=['tenk'], help='Run a built-in example project')
    args = parser.parse_args()

    if args.example == 'tenk':
        project_dir = TENK_PROJECT_DIR
        project_name = TENK_PROJECT_NAME
        sim_name = TENK_SIM_NAME
    elif args.project_dir and args.project_name and args.sim_name:
        project_dir = args.project_dir
        project_name = args.project_name
        sim_name = args.sim_name
    else:
        print("Error: You must specify either --example or all of --project-dir, --project-name, and --sim-name.")
        sys.exit(1)

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

    # Run the Java process
    try:
        subprocess.run(java_cmd, env=env, check=True)
        print(f"Simulation '{sim_name}' completed successfully for project '{project_name}' in directory '{project_dir}'.")
    finally:
        os.remove(script_path)

if __name__ == "__main__":
    main()
