#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
import os
import sys
import json

JYTHON_TEMPLATE = '''from hms.model.JythonHms import *
OpenProject("{project_name}", "{project_dir}")
ComputeRun("{sim_name}")
SaveAllProjectComponents()
'''

def main():
    parser = argparse.ArgumentParser(description="HEC-HMS CLI Runner")
    parser.add_argument('--project_file', type=str, help='Path to the .hms project file')
    parser.add_argument('--sim_name', type=str, help='Simulation name to run')
    parser.add_argument('--example', choices=['tenk'], help='Run a built-in example project')
    parser.add_argument('--json_file', type=str, help='Path to a JSON file with hms_schema')
    args = parser.parse_args()

    input_methods = sum([bool(args.example), bool(args.json_file), bool(args.project_file and args.sim_name)])
    if input_methods != 1:
        print("Error: Specify exactly one input method: --example, --json_file, or both --project_file and --sim_name.")
        sys.exit(1)

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
            print(f"Error reading or parsing JSON: {e}")
            sys.exit(1)
        if not hms_file or not sim_name:
            print("Error: JSON must contain hms_schema with project_file and sim_name.")
            sys.exit(1)
    else:
        hms_file = args.project_file
        sim_name = args.sim_name

    if not hms_file or not hms_file.lower().endswith('.hms'):
        print("Error: project_file must be a .hms file")
        sys.exit(1)
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

    # Run the Java process
    try:
        subprocess.run(java_cmd, env=env, check=True)
        print(f"Simulation '{sim_name}' completed successfully for project '{project_name}' in directory '{project_dir}'.")
    finally:
        os.remove(script_path)

if __name__ == "__main__":
    main()
