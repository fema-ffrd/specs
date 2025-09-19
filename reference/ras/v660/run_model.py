#!/usr/bin/env python3
import sys
import os
import json
import re
import subprocess
import shutil
import time
from pathlib import Path
from parsers.ras_unsteady import Config

DOWNLOAD = "/usr/local/bin/download"
UPLOAD = "/usr/local/bin/upload"
LOCAL_DIR = "/mnt"


def main(cfg):
    # Set up environment for RasUnsteady
    env = os.environ.copy()
    ras_lib_path = "/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8"
    ld = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = ras_lib_path + (os.pathsep + ld if ld else "")
    ras_exe_path = "/ras/bin"
    path = env.get("PATH", "")
    env["PATH"] = ras_exe_path + (os.pathsep + path if path else "")

    model_files = cfg.get_input_by_name("ras_model_files")
    # print(f"Model files input: {model_files}")
    attrs = cfg.attributes

    if cfg.store.store_type == "S3":
        # download from s3
        local_tmp_hdf = f"{LOCAL_DIR}/{model_files.paths.tmp_hdf}"
        # TODO: remove hardcoding
        try:
            subprocess.call(
                [
                    DOWNLOAD,
                    "b_file",
                    f"s3://trinity-pilot/{model_files.paths.b_file}",
                    f"{LOCAL_DIR}/{model_files.paths.b_file}",
                ]
            )
            subprocess.call(
                [
                    DOWNLOAD,
                    "o_file",
                    f"s3://trinity-pilot/{model_files.paths.o_file}",
                    f"{LOCAL_DIR}/{model_files.paths.o_file}",
                ]
            )
            subprocess.call(
                [
                    DOWNLOAD,
                    "x_file",
                    f"s3://trinity-pilot/{model_files.paths.x_file}",
                    f"{LOCAL_DIR}/{model_files.paths.x_file}",
                ]
            )
            subprocess.call(
                [
                    DOWNLOAD,
                    "tmp_hdf",
                    f"s3://trinity-pilot/{model_files.paths.tmp_hdf}",
                    local_tmp_hdf,
                ]
            )
        except Exception as e:
            print(f"Error downloading files: {e}")
            return 1
    elif cfg.store.store_type == "LOCAL":
        print("Using local files, no download needed.")
    else:
        print(f"Unsupported store type: {cfg.store.store_type}")
        return 1

    cmd = [f"{ras_exe_path}/RasUnsteady", local_tmp_hdf, f"x{attrs.geom}"]
    print(cmd)

    # Run RasUnsteady, stream output to stderr and check for success string
    success_phrase = "Finished Unsteady Flow Simulation"
    found_success = False
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True, bufsize=1)
    try:
        for line in proc.stdout:
            sys.stderr.write(line)
            sys.stderr.flush()
            if success_phrase in line:
                found_success = True
        proc.wait()
    except KeyboardInterrupt:
        proc.kill()
        proc.wait()
        sys.stderr.write("Interrupted\n")
        return 2

    if found_success and proc.returncode == 0:
        time.sleep(2)
        try:
            outputs = cfg.get_output_by_name("hdf_output")
            hdf_output_path = f"s3://trinity-pilot/{outputs.paths.hdf_output}"

            # TODO: remove hardcoding
            try:
                subprocess.call(
                    [
                        UPLOAD,
                        hdf_output_path,
                        "--path",
                        local_tmp_hdf,
                    ]
                )
                sys.stdout.write(f"RasUnsteady succeeded! Outputs uploaded successuflly!")
                return 0
            except Exception as e:
                print(f"Error uploading files: {e}")
                return 1

        except Exception as e:
            sys.stderr.write(f"Error moving file: {e}\n")
            return 2
    else:
        sys.stderr.write("Error: RasUnsteady failed.\n")
        return 2


if __name__ == "__main__":
    cfg = json.loads("".join(sys.argv[1:]))
    config = Config(**cfg)
    exit_code = main(config)
    sys.exit(exit_code)
